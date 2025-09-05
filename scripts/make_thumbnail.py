from PIL import Image
import math, os
from collections import Counter

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
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(".png")]
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


def process_root_folder(root_path):
    # Проходим по всем подпапкам
    for folder in os.listdir(root_path):
        folder_path = os.path.join(root_path, folder)
        if os.path.isdir(folder_path):  # только папки
            out_file = os.path.join(root_path, f"{folder}.png")
            make_collage_for_folder(folder_path, out_file)


# 🔹 Пример использования
# process_root_folder("../content/templates/1")


