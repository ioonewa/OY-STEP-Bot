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


async def append_photo_with_fade(
    photo_path: str,
    video_path: str,
    output_path: str,
    photo_duration: float = 4.0,
    fade_duration: float = 1.0,
) -> str:
    """
    Конец video_path + фото с кросс-фейдом (затухание/появление).
    """
    out = Path(output_path)
    tmp_photo = out.with_suffix(".fade_photo.mp4")

    # получаем параметры исходного видео
    v_fps, width, height = await _get_video_params(video_path)

    # фото -> ролик
    await _run_ffmpeg(
        "ffmpeg", "-y",
        "-loop", "1",
        "-t", str(photo_duration + fade_duration),  # запас для xfade
        "-i", photo_path,
        "-vf", f"scale={width}:{height}",
        "-r", str(v_fps),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(tmp_photo)
    )

    # узнаём длительность исходного видео
    probe = await _run_ffmpeg(
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=nk=1:nw=1",
        video_path
    )
    vid_dur = float(probe.decode().strip())

    # xfade: начинаем за fade_duration до конца
    await _run_ffmpeg(
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", str(tmp_photo),
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset={vid_dur - fade_duration}[v]",
        "-map", "[v]",
        "-map", "0:a?",  # если есть звук – копируем
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(out)
    )

    tmp_photo.unlink(missing_ok=True)
    return str(out)

async def append_photo_with_blink(
    photo_path: str,
    video_path: str,
    output_path: str,
    photo_duration: float = 4.0,
    fade_duration: float = 1.0,
) -> str:
    """
    Добавляет фото в конец видео с эффектом «моргания»:
    исходное видео плавно гаснет в чёрный, затем из чёрного появляется фото.
    """
    out = Path(output_path)
    tmp_photo = out.with_suffix(".blink_photo.mp4")

    # параметры исходного видео
    v_fps, width, height = await _get_video_params(video_path)

    # фото -> ролик (запас для fade)
    await _run_ffmpeg(
        "ffmpeg", "-y",
        "-loop", "1",
        "-t", str(photo_duration + fade_duration),
        "-i", photo_path,
        "-vf", f"scale={width}:{height}",
        "-r", str(v_fps),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(tmp_photo)
    )

    # длительность исходного видео
    probe = await _run_ffmpeg(
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=nk=1:nw=1",
        video_path
    )
    vid_dur = float(probe.decode().strip())

    # xfade: fadeblack — затухание в чёрный и появление из чёрного
    await _run_ffmpeg(
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", str(tmp_photo),
        "-filter_complex",
        (
            f"[0:v][1:v]xfade=transition=fadeblack:"
            f"duration={fade_duration}:"
            f"offset={vid_dur - fade_duration}[v]"
        ),
        "-map", "[v]",
        "-map", "0:a?",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(out)
    )

    tmp_photo.unlink(missing_ok=True)
    return str(out)


async def add_music_segment(
    video_path: str,
    music_path: str,
    output_path: str,
    start: float = 0.0,
    duration: float | None = None,
    music_volume: float = 1.0,
) -> str:
    """
    Накладывает музыку на видео.
    - start: секунда, с которой начинается музыка.
    - duration: длительность накладываемого фрагмента; если None — до конца ролика.
    - music_volume: множитель громкости музыки (1.0 = без изменений).
    Возвращает путь к output_path или выбрасывает ошибку с понятным текстом.
    """
    out = Path(output_path)

    # 1) Получаем длительность видео
    try:
        raw = await _run_ffmpeg(
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=nk=1:nw=1",
            video_path
        )
    except Exception as e:
        raise RuntimeError(f"Не удалось прочитать длительность видео ({video_path}): {e}")
    try:
        video_duration = float(raw.decode().strip())
    except Exception as e:
        raise RuntimeError(f"Некорректная длительность в ffprobe output для {video_path}: {e}")
    
    if duration is None:
        duration = video_duration
    else:
        duration = min(duration, video_duration)

    # ...
    if start < 0:
        raise ValueError("start не может быть отрицательным")

    # 2) вычисляем реальную длительность накладываемого фрагмента
    if duration is None:
        duration = video_duration
    else:
        duration = min(duration, video_duration)

    if duration <= 0:
        raise ValueError("Нечего накладывать: duration <= 0")

    if duration <= 0:
        raise ValueError("Нечего накладывать: вычисленная duration <= 0")

    # 3) Понимаем — есть ли у видео аудио (streams array non-empty)
    try:
        raw = await _run_ffmpeg(
            "ffprobe", "-v", "error",
            "-select_streams", "a",
            "-show_streams",
            "-of", "json",
            video_path
        )
        video_streams = json.loads(raw)
        video_has_audio = bool(video_streams.get("streams"))
    except Exception as e:
        # на этом этапе лучше считать, что аудио нет, но логируем/выбрасываем более конкретную ошибку
        raise RuntimeError(f"ffprobe failed checking audio streams for {video_path}: {e}")

    # 4) Узнаём количество каналов у музыки (нужно для корректного adelay)
    try:
        raw = await _run_ffmpeg(
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=channels",
            "-of", "json",
            music_path
        )
        music_info = json.loads(raw)
        if music_info.get("streams"):
            music_channels = int(music_info["streams"][0].get("channels", 1) or 1)
        else:
            music_channels = 1
    except Exception:
        # если не удалось — предполагаем минимум (1)
        music_channels = 1

    # 5) Строим filter_complex
    # 5) Строим filter_complex
    # музыка: отрезаем от 'start' до 'start+duration', громкость
    music_chain = (
        f"[1:a]atrim={start}:{start + duration},"
        f"asetpts=PTS-STARTPTS,volume={music_volume}[m]"
    )

    if video_has_audio:
        filter_complex = f"{music_chain};[0:a][m]amix=inputs=2:dropout_transition=0[a]"
        audio_map = "[a]"
    else:
        filter_complex = music_chain
        audio_map = "[m]"

    # 6) Собираем и запускаем ffmpeg
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", music_path,
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", audio_map,
        "-c:v", "copy",      # видео не перекодируем
        "-c:a", "aac", "-b:a", "192k",
        str(out)
    ]

    try:
        await _run_ffmpeg(*cmd)
    except Exception as e:
        # даём контекст — полезно при отладке ffmpeg stderr
        raise RuntimeError(f"ffmpeg failed while adding music to {video_path}: {e}")

    return str(out)
