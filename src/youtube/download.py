import os
import sys

from pytube import YouTube
from datetime import datetime
from pytube.cli import on_progress

CURRENT_TIME = datetime.now().strftime('%H%M%S')
DOWNLOAD_PATH = os.path.expanduser(r'~/Download/botcast')
EXT = '.mp4'


def single_download(url, file_name):
    if file_name:
        youtube_object = YouTube(url, on_progress)
        youtube_object.title = file_name

    video_name = f'{format_file_name(youtube_object.title)}'
    output_download = os.path.join(DOWNLOAD_PATH, video_name + CURRENT_TIME)

    video_name += EXT
    try:
        youtube_object.streams.filter(progressive=True, file_extension='mp4').order_by(
            'resolution').desc().first().download(output_path=output_download, filename=video_name)
    except:
        sys.exit(f'Falha no download do vídeo: "{video_name}".')

    video = os.path.join(output_download, video_name)

    return video


def format_file_name(file_name):
    return file_name[0:20].casefold().replace(' ', '')


def download_audio_video(url, file_name):
    if file_name:
        youtube_object = YouTube(url, on_progress)
        youtube_object.title = file_name

    video_name = f'{format_file_name(youtube_object.title)}'
    audio_name = f'audio_{video_name}'
    output_download = os.path.join(DOWNLOAD_PATH, video_name + CURRENT_TIME)

    try:
        youtube_object.streams.filter(adaptive=True).order_by('resolution').desc(
        ).first().download(output_path=output_download, filename=video_name)
    except:
        sys.exit(f'Falha no download do vídeo: "{video_name}".')
    try:
        youtube_object.streams.filter(adaptive=True, only_audio=True).order_by(
            'abr').desc().first().download(output_path=output_download, filename=audio_name)
    except:
        sys.exit(f'Falha no download do áudio: "{video_name}".')

    video_path = os.path.join(output_download, video_name)
    audio_path = os.path.join(output_download, audio_name)
    downloaded_files = {"video": video_path, "audio": audio_path}

    return downloaded_files
