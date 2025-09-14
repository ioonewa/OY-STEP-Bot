
from io import BytesIO
from pathlib import Path
from functools import lru_cache
from typing import Optional, Tuple, Dict, Any, Literal
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
from collections import Counter

import math, os
import asyncio
import logging


from Bot.utils.stash import stash_img 
from loader import database

# --- Конфигурация пула/семафора (можно настраивать) ---
CPU_COUNT = os.cpu_count() or 2
# Для CPU-bound задач лучше иметь примерно CPU_COUNT воркеров. Немного оставляем запас.
_DEFAULT_WORKERS = max(1, CPU_COUNT)
_executor = ThreadPoolExecutor(max_workers=_DEFAULT_WORKERS)
_semaphore = asyncio.Semaphore(_DEFAULT_WORKERS)

# Логгер
logger = logging.getLogger(__name__)

# --- добавленные константы и uncached reader ---
CACHEABLE_PREFIXES = (
    "content" ,       # шаблоны, маски, рамки, шрифты
    "content/for_bot",
    "content/templates",
)

def _read_file_bytes_uncached(path: str) -> bytes:
    """Читаем байты прямо с диска без кеша (для изменяемых файлов, например out_file)."""
    with open(path, "rb") as f:
        return f.read()

# -------------------------
# КЕШИРОВАНИЕ (уменьшает операции чтения с диска)
# - кешируем байты файлов (templates, masks, fonts)
# - не кешируем готовые Image объекты, потому что они mutable
# -------------------------
@lru_cache(maxsize=256)
def _read_file_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()

def _is_cacheable_path(path: str) -> bool:
    """
    Решение: кешируем только статические ресурсы в content/*;
    все остальные пути (photos/, temporary файлы) читаем напрямую.
    """
    p = Path(path)
    # нормализуем первый сегмент
    if not p.parts:
        return False
    first = p.parts[0]
    return first in ("content",)  # можно расширить при необходимости

@lru_cache(maxsize=64)
def _font_bytes(font_path: str) -> bytes:
    return _read_file_bytes(font_path)
# Утилиты для работы с изображениями (synchronous) — их вызывает executor
# -------------------------
def _open_image_from_bytes_rgba(data: bytes) -> Image.Image:
    """Открыть изображение из байтов и привести к RGBA."""
    img = Image.open(BytesIO(data))
    return img.convert("RGBA")

def _open_image_from_path_rgba(path: str) -> Image.Image:
    """
    Открываем изображение. Если путь попадает в кешируемые директории — читаем через cached `_read_file_bytes`.
    Если это изменяемый/временный файл (например photos/...), читаем напрямую (uncached),
    чтобы не получить "старую" версию из кэша.
    """
    if _is_cacheable_path(path):
        data = _read_file_bytes(path)
    else:
        data = _read_file_bytes_uncached(path)
    return _open_image_from_bytes_rgba(data)


def _ensure_parent_dir(file_path: str) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

# --- Core synchronous implementations (выполняются в threadpool) ---
def _overlay_photo_sync(
    top: int,
    left: int,
    rect_width: int,
    rect_height: int,
    frame_path: str,
    photo_path: str,
    mask_path: Optional[str] = None,   # PNG маска той же формы
    out_file: str = "out_file.png",
    angle: float = 0,
    rotate_expand_centered: bool = True  # улучшение: при expand=True сохраняем центр
) -> str:
    """
    Синхронная реализация наложения фотографии в рамку.
    Выполняется в executor чтобы не блокировать asyncio loop.
    """
    # Загружаем ресурсы (через кеш байтов)
    frame_img = _open_image_from_path_rgba(frame_path)
    photo_img = _open_image_from_path_rgba(photo_path)
    mask_img = None
    if mask_path:
        # Маска хранится как L (grayscale) — читаем байты и открываем
        mask_data = _read_file_bytes(mask_path)
        mask_img = Image.open(BytesIO(mask_data)).convert("L")

    # Масштабируем фото под размер прямоугольника (fill)
    scale_w = rect_width / photo_img.width
    scale_h = rect_height / photo_img.height
    scale = max(scale_w, scale_h)
    new_size = (max(1, int(photo_img.width * scale)), max(1, int(photo_img.height * scale)))
    photo_img = photo_img.resize(new_size, Image.LANCZOS)

    # Обрезка по центру чтобы ровно вписать в rect_width x rect_height
    left_crop = (photo_img.width - rect_width) // 2
    top_crop = (photo_img.height - rect_height) // 2
    photo_img = photo_img.crop((
        left_crop,
        top_crop,
        left_crop + rect_width,
        top_crop + rect_height
    ))

    # Поворот — если rotate_expand_centered=True и expand=True, мы сдвинем paste так,
    # чтобы центр повернутого изображения совпадал с центром исходного прямоугольника.
    if angle:
        # expand=True чтобы не обрезать углы
        photo_img = photo_img.rotate(angle, expand=True)

    # Добавляем альфу по маске (если есть)
    if mask_img:
        mask_resized = mask_img.resize(photo_img.size, Image.LANCZOS)
        photo_img.putalpha(mask_resized)

    # Подготовка рамки: делаем copy чтобы не модифицировать общий объект (безопасно для кэшей)
    frame_copy = frame_img.copy()

    # Если после rotate image стал больше, корректируем позицию, чтобы центр совпадал
    paste_x, paste_y = left, top
    if angle and rotate_expand_centered:
        # координаты центра исходного прямоугольника (на рамке)
        rect_cx = left + rect_width // 2
        rect_cy = top + rect_height // 2
        # координаты верхнего левого для фото так, чтобы его центр совпал с (rect_cx, rect_cy)
        paste_x = rect_cx - photo_img.width // 2
        paste_y = rect_cy - photo_img.height // 2

    # Вставляем (используем alpha-канал фото как маску)
    frame_copy.paste(photo_img, (paste_x, paste_y), photo_img)

    # Сохраняем файл (создаём директорию если нужно)
    _ensure_parent_dir(out_file)
    frame_copy.save(out_file, "PNG")
    return out_file


def _overlay_text_sync(
    text: str,
    file_path: str,
    font: Optional[str],
    font_size: int,
    color: Tuple[int, int, int, int],
    x: int,
    y: int,
    offset_x: int = 0,
    center: bool = False,
    upper: bool = False,
    fonts_base_dir: str = "content/fonts"
) -> str:
    """
    Синхронная реализация добавления текста на изображение.
    Шрифты загружаются из байтов (кешируются байты).
    """
    if not text:
        return file_path

    # Открываем изображение (работаем с файлом на диске — оригинал)
    img = _open_image_from_path_rgba(file_path)
    draw = ImageDraw.Draw(img)

    # Загружаем шрифт
    if font:
        font_path = os.path.join(fonts_base_dir, font)
        fb = _font_bytes(font_path)
        font_obj = ImageFont.truetype(BytesIO(fb), font_size)
    else:
        # дефолтный шрифт
        font_obj = ImageFont.load_default()

    # Подготовка текста
    if upper:
        text = text.upper()

    if center:
        img_w, img_h = img.size
        bbox = draw.textbbox((0, 0), text, font=font_obj)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = ((img_w - text_w) // 2) + offset_x

    # Сам рендер текста (fill принимает RGBA или RGB)
    print(f"Данные для рисования ({x}, {y}) - {text}, {font_obj}, {tuple(color)}")
    draw.text((x, y), text, font=font_obj, fill=tuple(color))

    # Сохраняем (перезаписываем тот же файл)
    _ensure_parent_dir(file_path)
    img.save(file_path, "PNG")
    return file_path


def _get_user_preview_sync(photo_path: str, radius: int = 60) -> str:
    """
    Синхронная функция формирования preview: затемнение, вставка кадра и (опционально) скруглённые углы.
    """
    # Загружаем фото и рамку (рамка маленькая, но кеш читается)
    photo = _open_image_from_path_rgba(photo_path)
    width, height = photo.size
    max_side = max(width, height)

    frame = _open_image_from_path_rgba("content/for_bot/frame.png")
    frame_size = round(max_side // 1.5)
    frame = frame.resize((frame_size, frame_size), Image.LANCZOS)

    # Центр фото (координаты прямоугольника)
    cx, cy = width // 2, height // 2
    left = cx - frame_size // 2
    top = cy - frame_size // 2
    right = cx + frame_size // 2
    bottom = cy + frame_size // 2

    # 1) затемнение
    dark = Image.new("RGBA", photo.size, (0, 0, 0, round(255 * 0.7)))
    base = photo.copy()
    # alpha_composite изменяет base in-place и ожидает одинаковый размер
    base.alpha_composite(dark)

    # 2) вырезаем кусок под рамку
    crop = photo.crop((left, top, right, bottom))

    # Если нужны скруглённые углы — создаём маску и вставляем
    if radius > 0:
        mask = Image.new("L", crop.size, 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle([0, 0, crop.size[0], crop.size[1]], radius=radius, fill=255)
        base.paste(crop, (left, top), mask)
    else:
        base.paste(crop, (left, top))

    # 3) накладываем рамку поверх
    base.paste(frame, (left, top), frame)

    # Сохраняем
    p = Path(photo_path)
    output_path = str(p.with_name(p.stem + "_preview.png"))
    _ensure_parent_dir(output_path)
    base.save(output_path, "PNG")
    return output_path

# -------------------------
# Async wrappers — вызывайте их из asyncio контекста (они не будут блокировать loop)
# -------------------------
async def _run_blocking(fn, *args, **kwargs):
    """
    Обёртка, которая:
      - Ограничивает параллельность через semaphore
      - Запускает callable в ThreadPoolExecutor
    """
    async with _semaphore:
        loop = asyncio.get_running_loop()
        # run_in_executor принимает (executor, func, *args)
        return await loop.run_in_executor(_executor, lambda: fn(*args, **kwargs))

# Публичные async функции (совместимы с оригинальным интерфейсом)
async def overlay_photo(
    top: int,
    left: int,
    rect_width: int,
    rect_height: int,
    frame_path: str,
    photo_path: str,
    mask_path: Optional[str] = None,
    out_file: str = "out_file.png",
    angle: float = 0,
    rotate_expand_centered: bool = True
) -> str:
    return await _run_blocking(
        _overlay_photo_sync,
        top, left, rect_width, rect_height,
        frame_path, photo_path, mask_path, out_file, angle, rotate_expand_centered
    )


async def overlay_text(
    text: str,
    file_path: str,
    font: Optional[str],
    font_size: int,
    color: Tuple[int, int, int, int],
    x: int,
    y: int,
    offset_x: int = 0,
    center: bool = False,
    upper: bool = False,
    fonts_base_dir: str = "content/fonts",
    **kwargs
) -> str:
    return await _run_blocking(
        _overlay_text_sync,
        text, file_path, font, font_size, color, x, y, offset_x, center, upper, fonts_base_dir
    )

async def get_user_preview(photo_path: str, radius: int = 60) -> str:
    return await _run_blocking(_get_user_preview_sync, photo_path, radius)

# -------------------------
# Верхний уровень: get_personal_photo (сохранена асинхронной, но теперь использует async overlay_* версии)
# -------------------------
async def get_personal_photo(
    user_data: Dict[str, Any],
    style: str,
    post_id: str,
    telegram_id: int,
    obj: Literal["post", "story"]
) -> str:
    """
    Асинхронный рабочий поток: персонализирует изображение и возвращает file_id от stash_img.
    Замечание: stash_img в вашем коде — async; используем await.
    """
    frame_path = f"content/templates/{post_id}/{style}/{obj}/6.png"
    out_file = f"photos/{telegram_id}/{post_id}_{obj}_{style}.png"

    # Убедимся, что директория есть (асинхронно это быстрый вызов; IO внутри executor)
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)

    rules = await database.get_content_rules(int(post_id), obj)
    base_font = rules["font"]

    # Накладываем фотографию
    await overlay_photo(
        **rules['photo'],
        frame_path=frame_path,
        photo_path=user_data['photo_source'],
        out_file=out_file
    )

    # Специальные правила
    if str(post_id) == "5" and obj == "post":
        # Накладываем круг поверх фотографии (дизайнерский элемент)
        await overlay_photo(
            top=-56,
            left=443,
            rect_width=187,
            rect_height=187,
            frame_path=out_file,
            photo_path="content/for_bot/Ellipse.png",
            out_file=out_file
        )

    # Добавляем надписи на фотографию
    for text_key, params in rules.get("text", {}).items():
        data = user_data.get(text_key)
        if not data:
            continue
        if text_key == "username":
            data = f"@{data}"

        # собираем словарь заново, не мутируя base_font
        font_args = {
            "font":  base_font["name"],
            "font_size": base_font["size"],
            "color": base_font["color"][style],
            "center": base_font.get('center', False),
            "offset_x": base_font.get('offset_x', 0),
            "upper": base_font.get('upper', False)
        }

        await overlay_text(
            text=data,
            file_path=out_file,
            **font_args,
            **params,
        )

    # # Кешируем фотографию для telegram
    file_id = await stash_img(out_file)
    return file_id

# (Дополнительно) функция для graceful shutdown executor (если нужно)
def shutdown_image_executor(wait: bool = False):
    """Вызвать при завершении приложения если нужно освободить потоковый пул."""
    try:
        _executor.shutdown(wait=wait)
    except Exception:
        logger.exception("Error while shutting down image executor")


MAX_SIZE = 1024  # максимальный размер итогового коллажа (ширина/высота)

def get_dominant_color(image, resize=50):
    """Возвращает самый часто встречающийся цвет изображения"""
    img = image.copy()
    img.thumbnail((resize, resize))
    pixels = list(img.getdata())
    pixels = [p[:3] for p in pixels if len(p) >= 3]  # убираем прозрачность
    most_common = Counter(pixels).most_common(1)[0][0]
    return most_common


def make_collage_for_folder(folder_path, out_file) -> str:
    # Собираем все PNG файлы
    files = [f for f in os.listdir(folder_path) if (f.lower().endswith(".png") and int(f[0]) < 7)]
    files.sort()

    if not files:
        print(f"⚠️ В папке {folder_path} нет PNG файлов!")
        return

    # Загружаем изображения
    images = [Image.open(os.path.join(folder_path, f)).convert("RGBA") for f in files]

    # Размер первой фотографии (берём за эталон)
    w, h = images[0].size
    n = len(images)

    # Фон по первой фотке
    bg_color = get_dominant_color(images[0])

    # Колонки и строки
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    # Создаём холст
    canvas = Image.new("RGBA", (cols * w, rows * h), bg_color + (255,))

    # Вставляем фото
    for idx, img in enumerate(images):
        row = idx // cols
        col = idx % cols
        canvas.paste(img, (col * w, row * h), img)

    # Если итоговый размер превышает MAX_SIZE → уменьшаем с сохранением пропорций
    if canvas.width > MAX_SIZE or canvas.height > MAX_SIZE:
        canvas.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)

    # Сохраняем
    canvas.save(out_file)
    print(f"✅ Коллаж сохранён: {out_file}")
    return out_file
