from distutils.log import error
import json
import os
import click


from bots.single_bot import initialize_bot
from bots.multiple_bots import initialize_mbot
from bots.single_bot import BOTCAST_PATH
from cli.validations import validate_ranges
from cli.validations import validate_url
from cli.validations import validate_name


from bots.multiple_bots import AUTOMATION_DATA_PATH


@click.group('cli')
def cli():
    ...


@cli.command('init')
def init():
    automation_data = {
        "videos": [
            {
                "url": "[url do vídeo]",
                "ranges": "[início do corte, fim do corte]",
                "name": "[nome do vídeo]",
                "highest": "[máxima qualidade]"
            }
        ]
    }

    if not os.path.exists(BOTCAST_PATH):
        os.mkdir(BOTCAST_PATH)

    if not os.path.exists(AUTOMATION_DATA_PATH):
        with open(AUTOMATION_DATA_PATH, 'w') as f:
            json.dump(automation_data, f)


@cli.command('botcast')
@click.option(
    '-u', '--url',
    callback=validate_url,
    type=click.STRING,
    required=True,
    help='Url do vídeo para download.',

)
@click.option(
    '-r', '--ranges',
    callback=validate_ranges,
    required=True,
    multiple=True,
    help='Agrupamento dos intervalos (início, fim) dos cortes. Ex: 5, 10, 15, 25'
)
@click.option(
    '-as', '--name',
    callback=validate_name,
    default=None,
    type=click.STRING,
    help='Nome do vídeo que será baixado.'
)
@click.option(
    '-h', '--highest',
    is_flag=True,
    type=click.BOOL,
    help='Indica que o conteúdo do YouTube deverá ser baixado com a maior qualidade disponível'
)
def botcast(url, ranges, name, highest):
    """Automação para um único vídeo."""
    initialize_bot(url, ranges, name, highest)


@cli.command('mbotcast')
def mbotcast():
    """Automação para múltiplos vídeos configurados em: 'automation_data.json'"""

    if not os.path.exists(AUTOMATION_DATA_PATH):
        raise click.BadParameter(
            f'O arquivo automation_data.json não foi encontrado. Execute: mbotcast-init" e configure seu arquivo em {AUTOMATION_DATA_PATH}')

    initialize_mbot()
