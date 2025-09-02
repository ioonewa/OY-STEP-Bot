from PIL import Image, ImageDraw, ImageFont

from .stash import stash_img

def overlay_photo(
        top: int,
        left: int,
        rect_width: int,
        rect_height: int,
        frame_path: str,
        photo_path: str,
        out_file:str,
        angle: float = 0
    ):
    # Загружаем рамку и фото
    frame = Image.open(frame_path).convert("RGBA")
    photo = Image.open(photo_path).convert("RGBA")

    # Масштабирование с сохранением пропорций, заполнение всего прямоугольника
    scale_w = rect_width / photo.width
    scale_h = rect_height / photo.height
    scale = max(scale_w, scale_h)  # берём максимум, чтобы заполнить весь прямоугольник
    new_size = (int(photo.width * scale), int(photo.height * scale))
    photo_resized = photo.resize(new_size, Image.LANCZOS)

    # Обрезка лишнего, чтобы вписать ровно в прямоугольник
    left_crop = (photo_resized.width - rect_width) // 2
    top_crop = (photo_resized.height - rect_height) // 2
    photo_cropped = photo_resized.crop((
        left_crop,
        top_crop,
        left_crop + rect_width,
        top_crop + rect_height
    ))

    # Поворот (expand=True, чтобы не обрезались углы)
    photo_rotated = photo_cropped.rotate(angle, expand=True)

    # Вставка в рамку
    frame.paste(photo_rotated, (left, top), photo_rotated)

    # Сохраняем результат
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
):
    frame = Image.open(file_path).convert("RGBA")
    # Добавление текста
    if text:
        draw = ImageDraw.Draw(frame)
        if font:
            font = ImageFont.truetype(font, font_size)
        else:
            font = ImageFont.load_default()

        draw.text((text_x, text_y), text, font=font, fill=color)

    # Сохраняем
    frame.save(file_path)

    return file_path

async def get_personal_photo(
    telegram_id: int,
    user_data: dict,
    post_id: int,
    style: str
) -> str:
    """
    Функция персонализирует и высылает пользователю контент
    для поста по заданному стилю

    Пока это скорее заглушка
    """
    frame_path = f"content/templates/{post_id}/{style}/post/frame.png"
    out_file=f"photos/{telegram_id}/{post_id}_{style}.png"
    font_path = f"content/templates/{post_id}"

    if style == "Blue":
        overlay_photo(
            top=291,
            left=109,
            rect_width=862,
            rect_height=532,
            frame_path=frame_path,
            photo_path=user_data['photo_source'],
            out_file=out_file
        )
        # Имя
        color = (255,255,255,255)
        font = f"{font_path}/TT Interphases Pro Mono Trial Var Roman.ttf"
        overlay_text(
            text=user_data['name'],
            file_path=out_file,
            font=font,
            font_size=58,
            color=color,
            text_x=224,
            text_y=900.
        )
        # Почта
        overlay_text(
            text=user_data['email'],
            file_path=out_file,
            font=font,
            font_size=58,
            color=color,
            text_x=224,
            text_y=970
        )
        # Номер телефона
        overlay_text(
            text=user_data['phone_number'],
            file_path=out_file,
            font=font,
            font_size=58,
            color=color,
            text_x=224,
            text_y=1049
        )
        # Ник тг
        overlay_text(
            text=f"@{user_data['username']}",
            file_path=out_file,
            font=font,
            font_size=58,
            color=color,
            text_x=224,
            text_y=1125
        )
    elif style == "Red":
        overlay_photo(
            top=109,
            left=196,
            rect_width=605,
            rect_height=600,
            angle=5,
            photo_path=user_data['photo_source'],
            frame_path=frame_path,
            out_file=out_file
        )
        # Ник тг
        color = (0,0,0,255)
        font = f"{font_path}/Roboto_Bold.ttf"
        overlay_text(
            text=f"@{user_data['username']}",
            file_path=out_file,
            font=font,
            font_size=80,
            color=color,
            text_x=286,
            text_y=913
        )
    elif style == "Black":
        overlay_photo(
            top=177,
            left=135,
            rect_width=811,
            rect_height=741,
            frame_path=frame_path,
            photo_path=user_data['photo_source'],
            out_file=out_file
        )
        # Ник тг
        color = (255,255,255,255)
        font = f"{font_path}/Roboto_Bold.ttf"
        overlay_text(
            text=f"@{user_data['username']}",
            file_path=out_file,
            font=font,
            font_size=80,
            color=color,
            text_x=265,
            text_y=1067
        )
    
    file_id = await stash_img(out_file)
    return file_id
    




