import subprocess
from pathlib import Path
from moviepy import VideoFileClip  # только для чтения fps/размера
from typing import List, Dict, Optional

import asyncio
import json

import logging

logger = logging.getLogger(__name__)

def photos_to_video(
    photos: List[Dict[str, float]],
    output_path: str,
    reference_video: str | None = None,
    fps: int | None = None,
    size: tuple[int, int] | None = (1080, 1920),
) -> str:
    """
    Склеивает список фотографий в один mp4-файл.

    photos: список словарей вида:
        [
          {"path": "img1.jpg", "duration": 3.0},
          {"path": "img2.png", "duration": 5.5},
          ...
        ]
    output_path: путь к финальному видео.
    reference_video: если указан — берём fps/размер из этого видео для унификации.
    fps: частота кадров, если не указан reference_video.
    size: (width, height), если не указан reference_video.
    """
    if not photos:
        raise ValueError("Список фотографий пуст")

    # 1️⃣ Определяем fps и размер
    if reference_video:
        ref = VideoFileClip(reference_video)
        if fps is None:
            fps = int(round(ref.fps))
        if size is None:
            size = tuple(ref.size)
        ref.close()
    if fps is None:
        fps = 25  # дефолт
    if size is None:
        raise ValueError("Укажите size или reference_video для определения размера.")

    out = Path(output_path)
    tmp_dir = out.parent
    concat_file = out.with_suffix(".txt")

    # 2️⃣ Генерируем временные mp4 для каждой фотографии
    tmp_clips = []
    for idx, item in enumerate(photos):
        photo = item["path"]
        dur = float(item["duration"])
        tmp_clip = tmp_dir / f"photo_{idx}.tmp.mp4"
        tmp_clips.append(tmp_clip)

        subprocess.run([
            "ffmpeg", "-y",
            "-loop", "1",
            "-t", str(dur),
            "-i", photo,
            "-vf", f"scale={size[0]}:{size[1]}",
            "-r", str(fps),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            str(tmp_clip)
        ], check=True)

    # 3️⃣ Создаём список для concat
    concat_file.write_text(
        "\n".join(f"file '{clip.resolve()}'" for clip in tmp_clips),
        encoding="utf-8"
    )

    # 4️⃣ Склеиваем без перекодирования
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(out)
    ], check=True)

    # 5️⃣ Чистим временные файлы
    for clip in tmp_clips:
        clip.unlink(missing_ok=True)
    concat_file.unlink(missing_ok=True)

    return str(out)

async def _run_ffmpeg(*args: str) -> None:
    """
    Запуск ffmpeg/ffprobe без блокировки event loop.
    Бросает исключение, если код возврата != 0.
    """
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(args)}\n"
            f"stderr: {stderr.decode(errors='ignore')}"
        )
    return stdout

async def _get_video_params(video_path: str) -> tuple[int, int, int]:
    """
    Получает (fps, width, height) через ffprobe.
    """
    probe_cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate,width,height",
        "-of", "json",
        video_path
    ]
    raw = await _run_ffmpeg(*probe_cmd)
    data = json.loads(raw)
    s = data["streams"][0]
    # fps приходит как "num/den"
    num, den = map(int, s["r_frame_rate"].split("/"))
    fps = round(num / den) if den else num
    return fps, s["width"], s["height"]

async def append_photo_to_video(
    photo_path: str,
    video_path: str,
    output_path: str,
    photo_duration: float = 4.0,
    fps: Optional[int] = None
) -> str:
    """
    Асинхронно добавляет фото в конец видео на photo_duration секунд.
    * photo_path – путь к фото
    * video_path – исходное видео
    * output_path – финальный mp4
    * photo_duration – длительность вставки
    * fps – если None, берём из исходного видео
    """
    out = Path(output_path)
    tmp_photo_video = out.with_suffix(".photo_tmp.mp4")
    tmp_list = out.with_suffix(".txt")

    # 1️⃣ Получаем параметры исходного видео
    v_fps, width, height = await _get_video_params(video_path)
    if fps is None:
        fps = v_fps

    logger.info(f"Исходный размер для видер - {width} x {height}")

    # 2️⃣ Генерируем mp4 из фото
    await _run_ffmpeg(
        "ffmpeg", "-y",
        "-loop", "1",
        "-t", str(photo_duration),
        "-i", photo_path,
        "-vf", f"scale={width}:{height}",
        "-r", str(fps),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        str(tmp_photo_video)
    )

    # 3️⃣ Создаём список для concat
    tmp_list.write_text(
        f"file '{Path(video_path).resolve()}'\n"
        f"file '{tmp_photo_video.resolve()}'\n",
        encoding="utf-8"
    )

    # 4️⃣ Склеиваем без перекодирования
    await _run_ffmpeg(
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(tmp_list),
        "-c", "copy",
        str(out)
    )

    # 5️⃣ Чистим временные файлы
    tmp_photo_video.unlink(missing_ok=True)
    tmp_list.unlink(missing_ok=True)

    return str(out)
