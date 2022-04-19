import json
import os
import concurrent.futures

from cli.validations import validate_ranges
from cli.validations import validate_url
from cli.validations import validate_name
from cli.validations import validate_highest
from utils.util import clear_tempfiles
from youtube.upload import initialize_upload

from bots.single_bot import initialize_bot
from bots.single_bot import BOTCAST_PATH, CLIPS_PATHS

AUTOMATION_DATA_PATH = os.path.join(BOTCAST_PATH, 'automation_data.json')


def initialize_mbot():
    with open(CLIPS_PATHS, 'w') as f:
        pass

    try:
        with open(AUTOMATION_DATA_PATH, 'r') as f:
            file_data = json.load(f)
            automation_data = file_data['videos']

        automation_data = validate_automation_data(automation_data)
    except IOError as e:
        raise IOError(
            'Arquivo automation_data.json não encontrado ou uma das suas informações de url,ranges,name e highest está inválida.')

    concurrently_process(automation_data)
    initialize_upload(CLIPS_PATHS)


def validate_automation_data(automation_data):
    aux_automation_data = []

    for video_data in automation_data:
        ranges = validate_ranges(None, None, video_data['ranges'])
        url = validate_url(None, None, video_data['url'])
        name = validate_name(None, None, video_data['name'])
        highest = validate_highest(video_data['highest'])
        aux_automation_data.append(
            {'url': url, 'ranges': ranges, 'name': name, 'highest': highest})
        for data in aux_automation_data:
            for key, value in data.items():
                if value == None:
                    print(f'A informação "{key}:{value}" inserida não é válida.')

    return aux_automation_data


def concurrently_process(automation_data):
    # Essa função realiza a execução concorrente do bot principal usando 3 threads,
    # uma vez que essa implementação obteve uma performance superior as soluções
    # com menos,nenhuma ou mais threads no contexto da automação de vários vídeos.

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for video_data in automation_data:
            futures.append(executor.submit(initialize_bot,
                                           url=video_data['url'],
                                           ranges=video_data['ranges'],
                                           name=video_data['name'],
                                           highest=video_data['highest']))
            clear_tempfiles()
