from PIL import Image, ImageDraw, ImageFont
from typing import List

from .stash import stash_img

from .templates_rules import rules

import os

def overlay_photo(
        top: int,
        left: int,
        rect_width: int,
        rect_height: int,
        frame_path: str,
        photo_path: str,
        mask_path: str= None,   # PNG маска той же формы
        out_file: str= "out_file.png",
        angle: float = 0
    ):
    # Загружаем
    frame = Image.open(frame_path).convert("RGBA")
    photo = Image.open(photo_path).convert("RGBA")
    if mask_path:
        mask = Image.open(mask_path).convert("L")  # ч/б маска
    else:
        mask = None

    # Масштабируем фото под размер маски
    scale_w = rect_width / photo.width
    scale_h = rect_height / photo.height
    scale = max(scale_w, scale_h)  # берём максимум, чтобы заполнить весь прямоугольник
    new_size = (int(photo.width * scale), int(photo.height * scale))
    photo = photo.resize(new_size, Image.LANCZOS)

    # Обрезка лишнего, чтобы вписать ровно в прямоугольник
    left_crop = (photo.width - rect_width) // 2
    top_crop = (photo.height - rect_height) // 2
    photo = photo.crop((
        left_crop,
        top_crop,
        left_crop + rect_width,
        top_crop + rect_height
    ))

    # Поворачиваем (если нужно)
    photo = photo.rotate(angle, expand=True)
    # Добавляем альфу по маске
    if mask:
        mask = mask.resize(photo.size, Image.LANCZOS)
        photo.putalpha(mask)

    # Вставляем в рамку
    frame.paste(photo, (left, top), photo)
    frame.save(out_file)
    return out_file

def overlay_text(
    text: str,
    file_path: str,
    font: str,
    font_size: int,
    color: tuple,
    text_x: int,
    text_y: int,
    offset_x: int = 0,
    center: bool = False,
    upper: bool = False
):
    frame = Image.open(file_path).convert("RGBA")
    # Добавление текста
    if text:
        draw = ImageDraw.Draw(frame)
        if font:
            font = ImageFont.truetype(f"content/fonts/{font}", font_size)
        else:
            font = ImageFont.load_default()

        if center:
            # размеры изображения
            img_w, img_h = frame.size

            # размеры текста через textbbox
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

            # координаты по центру
            text_x = ((img_w - text_w) // 2) + offset_x

        if upper:
            text = text.upper()

        draw.text((text_x, text_y), text, font=font, fill=color)

    # Сохраняем
    frame.save(file_path)

    return file_path

def get_user_preview(
        photo_path: str,
        radius: int = 60
    ) -> str:
    # Загружаем фото
    photo = Image.open(photo_path).convert("RGBA")
    width, height = photo.size
    max_side = max(width, height)

    # Загружаем рамку
    frame = Image.open("content/for_bot/frame.png").convert("RGBA")
    frame_size = round(max_side // 1.5)
    frame = frame.resize((frame_size, frame_size), Image.LANCZOS)

    # Центр фото
    cx, cy = width // 2, height // 2
    left = cx - frame_size // 2
    top = cy - frame_size // 2
    right = cx + frame_size // 2
    bottom = cy + frame_size // 2

    # 1. Накладываем затемнение на всю фотографию
    dark = Image.new("RGBA", photo.size, (0, 0, 0, round(255 * 0.7)))
    base = photo.copy()
    base.alpha_composite(dark)

    # 2. Вырезаем кусок из оригинала под рамку
    crop = photo.crop((left, top, right, bottom))

    # Если нужны скруглённые углы — добавляем маску
    if radius > 0:
        mask = Image.new("L", crop.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, crop.size[0], crop.size[1]], radius=radius, fill=255)
        base.paste(crop, (left, top), mask)
    else:
        base.paste(crop, (left, top))

    # 3. Накладываем рамку поверх
    base.paste(frame, (left, top), frame)

    # Сохраняем результат
    output_path = os.path.splitext(photo_path)[0] + "_preview.png"
    base.save(output_path, "PNG")

    return output_path

async def get_personal_photo(
    user_data: dict,
    style: str,
    post_id: str,
    telegram_id: int,
    obj: str
) -> str:
    """
    Функция персонализирует и высылает пользователю контент
    для поста по заданному стилю

    Пока это скорее заглушка
    """
    frame_path = f"content/templates/{post_id}/{style}/{obj}/6.png"
    out_file=f"photos/{telegram_id}/{post_id}_{style}.png"
    
    rules_obj = rules[f"{post_id}"][obj]
    font =  rules_obj["font"]
    text_colors = rules[f"{post_id}"]["text_colors"]

    overlay_photo(
        **rules_obj['photo'],
        frame_path=frame_path,
        photo_path=user_data['photo_source'],
        out_file=out_file
    )

    if str(post_id) == "5" and obj == "post":
        overlay_photo(
            top=-56,
            left=443,
            rect_width=187,
            rect_height=187,
            frame_path=out_file,
            photo_path="content/for_bot/Ellipse.png",
            out_file=out_file,
            corner_radius=1000
        )

    for text, params in rules_obj["text"].items():
        data = user_data.get(text)
        if not data:
            continue

        if text == "username":
            data = f"@{data}"
        
        overlay_text(
            text=data,
            file_path=out_file,
            font=font["name"],
            font_size=font["size"],
            offset_x=font.get("offset_x", 0),
            center=font.get("center", False),
            upper=font.get("upper", False),
            color=text_colors[style],
            **params
        )
        
    file_id = await stash_img(out_file)
    return file_id
    




