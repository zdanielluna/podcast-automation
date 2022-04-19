import os
from moviepy.editor import *

EXT = '.mp4'
KEYWORD = 'newclip'


def initialize_cut(ranges, video_path, audio_path=None):
    clips_folder = create_clips_folder(video_path)

    aux = 0
    clips_paths = []
    while(aux < len(ranges)-1):
        start = ranges[aux]
        end = ranges[aux + 1]

        output_path = build_clip_path(video_path, clips_folder)

        clip_path = cut(start, end, output_path, video_path, audio_path)
        clips_paths.append(clip_path)

        aux += 2

    return clips_paths


def create_clips_folder(video_path):
    clips_folder = os.path.join(os.path.dirname(video_path), 'clips')
    if not os.path.exists(clips_folder):
        os.mkdir(clips_folder)

    return clips_folder


def build_clip_path(video_path, clips_folder):
    video_name = os.path.basename(video_path)
    name_id = str(build_name_id(clips_folder))
    video_name = KEYWORD + name_id + '_' + video_name + EXT \
        if not EXT in video_name else KEYWORD + name_id + '_' + video_name

    output_path = os.path.join(clips_folder, video_name)

    return output_path


def cut(start, end, output_path, video_path, audio_path=None):
    with VideoFileClip(video_path) as videoclip:
        if audio_path:
            try:
                audioclip = AudioFileClip(audio_path)
                videoclip.audio = CompositeAudioClip([audioclip])
            except:
                sys.exit(
                    f'Ocorreu um erro ao tentar montar o vídeo: "{video_path}".')
        try:
            new_videoclip = videoclip.subclip(start, end)
            new_videoclip.write_videofile(output_path, codec="libx264")
        except:
            sys.exit(
                f'Falha ao tentar realizar o corte para "{video_path}". Verifique se o tempo do corte está dentro do tempo total do vídeo.')

    return output_path


def build_name_id(path):
    clips = os.listdir(path)
    if not clips:
        return 1

    name_ids = []
    for filename in clips:
        for char in filename[:filename.find('_')]:
            if char.isnumeric():
                name_ids.append(char)

    new_id = int(max(name_ids)) + 1

    return new_id
