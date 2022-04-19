import httplib2
import os
import random
import sys
import time

from cli.cli_upload import request_upload_data as cli_request_upload_data
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# Informa explicitamente a biblioteca HTTP para não tentar novamente, uma vez que
# o tratamento da lógica de tentativas está sendo feito por nós mesmos
httplib2.RETRIES = 1

# Número máximo de tentativas antes de desistir
MAX_RETRIES = 10

# Tenta todas as vezes que essas exceções forem disparadas
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Tenta todas as vezes que um apiclient.errors.HttpError é disparado
# com um desses códigos de status
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# A constante CLIENT_SECRETS_FILE especifica on nome do arquivo que contém
# as informações do OAuth 2.0 para essa aplicação, incluindo o client_id e o
# client_secret. Você pode adquirir o OAuth 2.0 client ID e o client secret a
# partir do console do Google API em: https://console.developers.google.com

# Por gentileza garanta que você habilitou o YouTube Data API para o seu projeto.
# Para mais informações de como utilizar o OAuth2 para acessar o YouTube Data API
# verifique em: https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

CLIENT_SECRETS_FILE = 'client_secrets.json'
# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.

# Esse escopo do OAuth 2.0 permite que a aplicação faça o upload de vídeos para o
# o canal do YouTube do usuário autenticado, mas não permite outros tipos de acesso.
YOUTUBE_UPLOAD_SCOPE = 'https://www.googleapis.com/auth/youtube.upload'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
MISSING_CLIENT_SECRETS_MESSAGE = """
AVISO: Por favor configure o OAuth 2.0

Para executar esse exemplo, você precisará preencher o arquivo client_secrets.json em:

   %s

com as informações da API Console
https://console.developers.google.com/

Para mais informações sobre o formato do arquivo client_secrets.json, visite:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')


def initialize_upload(clips_paths_file):
    try:
        with open(clips_paths_file, 'r') as f:
            lines = f.readlines()
            for video_path in lines:
                print(f'\nCriação de dados de upload para: {os.path.basename(video_path)}')
                upload_info = create_upload_data(video_path)
                start_upload(upload_info)
    except IOError:
        print(f'Arquivo clips.txt não encontrado.')


def create_upload_data(video_path):
    upload_info = {}
    upload_info = cli_request_upload_data()
    upload_info['file'] = video_path.replace('\n', '')

    return upload_info


def start_upload(video_info):
    # resolve o conflito com o argv da ferramenta CLICK
    del sys.argv[1:]
    args = argparser.parse_args()
    youtube = get_authenticated_service(args)

    try:
        upload(youtube, video_info)
    except HttpError as e:
        exit(f'Um erro HTTP {e.resp.status} ocorreu:\n{e.content}')


def get_authenticated_service(args):
    flow = flow_from_clientsecrets(
        os.path.abspath(os.path.join(
            os.path.dirname(__file__), CLIENT_SECRETS_FILE)),
        scope=YOUTUBE_UPLOAD_SCOPE,
        message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage(f'{sys.argv[0]}-oauth2.json')
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


def upload(youtube, options):
    tags = None
    if options['keywords']:
        tags = options['keywords'].split(',')

    body = dict(
        snippet=dict(
            title=options['title'],
            description=options['description'],
            tags=tags,
            categoryId=options['category'],
        ),
        status=dict(
            privacyStatus=options['privacyStatus']
        )
    )

    # Invoca o método videos.insert para criar e upar o vídeo.
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        # O parâmetro "chunksize" especifica em bytes o tamanho de cada pedaço
        # de dado que será enviado de cada vez. Configure o valor mais alto para
        # conexões mais confiáveis, uma vez que menos blocos levam a uploads mais
        # rápidos. Defina uma valor mais baixo para uma melhor recuperação em conexões
        # menos confiáveis.

        # Configurar "chunksize" igual a -1 no código abaixo significa que todo o arquivo
        # será carregado em uma única solicitação HTTP. (Se o upload falhar, ele será
        # realizado novamente a partir de onde ele parou). Geralmente essa é a melhor
        # prática, mas se você estiver utilizando um Python superior a versão 2.6 ou se
        # estiver em execução no App Engine, você deve definir o tamanho do bloco para
        # algo como 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(options['file'], chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request, options)


def resumable_upload(insert_request, options):
    # Esse método implementa a estratégia "exponential backoff" referente a
    # falha no upload.
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print(f'Realizando o upload...')
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print(f'O corte "{options["title"]}" foi enviado com sucesso.')
                else:
                    exit(f'O upload falhou com uma resposta inesperada: {response}')
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f'Um erro HTTP {e.resp.status} ocorreu:\n{e.content}'
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f'Um novo erro HTTP ocorreu: {e}'

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit('Não serão realizadas novas tentativas.')

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print(f'Aguardando {sleep_seconds} segundos para tentar novamente...')
            time.sleep(sleep_seconds)
