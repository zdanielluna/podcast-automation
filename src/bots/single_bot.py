import inspect
import os
import click

from youtube.download import single_download
from youtube.download import download_audio_video
from editor.edit_video import initialize_cut
from youtube.upload import initialize_upload


BOTCAST_PATH = os.path.expanduser(r'~/Download/botcast')
CLIPS_PATHS = os.path.join(BOTCAST_PATH, 'clips.txt')


def initialize_bot(url, ranges, name, highest):
    if highest == True:
        click.echo(f'Baixando áudio e vídeo "{name}"...')
        downloaded_files = download_audio_video(url, file_name=name)
        clips_paths = initialize_cut(ranges, downloaded_files['video'], downloaded_files['audio'])

    else:
        click.echo(f'Baixando vídeo {name}...')
        video_path = single_download(url, file_name=name)
        clips_paths = initialize_cut(ranges, video_path)

    caller = list(inspect.stack()[1])
    if not is_allowed_caller(caller):
        write_paths_to_file(CLIPS_PATHS, clips_paths, mode='a')
    else:
        write_paths_to_file(CLIPS_PATHS, clips_paths, mode='w')
        initialize_upload(CLIPS_PATHS)

    remove_duplicates_from_file(CLIPS_PATHS)


def is_allowed_caller(caller):
    forbidden_callers = ['thread.py', 'multiple_bots.py']
    forbidden_functions = ['run', 'initialize_mbot']

    caller_function = caller[3]
    caller_file = os.path.basename(caller[1])

    return True if caller_file not in forbidden_callers or \
        caller_function not in forbidden_functions else False


def remove_duplicates_from_file(filename):
    lines = []
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f]

    lines = set(lines)
    open(filename, 'w').write('\n'.join(lines) + '\n')


def write_paths_to_file(output, paths, mode='w'):
    with open(output, mode) as f:
        for path in paths:
            f.write(f'{path}\n')
