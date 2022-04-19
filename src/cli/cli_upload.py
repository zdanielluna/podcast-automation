import click

from cli.validations import validate_category
from cli.validations import validate_privacy_status
from cli.validations import validate_title


PRIVACY_STATUS_OPTIONS = """
Options: 'private', 'public' or 'unlisted'
"""
CATEGORY_OPTIONS = """
----- Category List -----

1 - Film & Animation,
2 - Autos & Vehicles,
10 - Music,
15 - Pets & Animals,
17 - Sports,
19 - Travel & Events,
20 - Gaming,
22 - People & Blogs,
23 - Comedy,
24 - Entertainment,
25 - News & Politics,
26 - Howto & Style,
27 - Education,
28 - Science & Technology,
29 - Nonprofits & Activism

"""


def request_title():
    title = None
    while not title:
        title = validate_title(click.prompt('Título', type=str))
        if not title:
            click.echo('Erro: o título não pode ser vazio.')

    return title


def request_category():
    category = None
    while not category:
        category = validate_category(click.prompt('Categoria', type=int))
        if not category:
            click.echo('Erro: a categoria inserida deve ser uma das opções disponíveis.')

    return str(category).replace('\n', '')


def request_privacy_status():
    privacy_status = None
    while not privacy_status:
        privacy_status = validate_privacy_status(click.prompt('Privacidade', type=str))
        if not privacy_status:
            click.echo('Erro: o "Privacy Status" deve ser uma das opções disponíveis.')
        else:
            return privacy_status.replace('\n', '')


def request_upload_data():
    upload_data = {}

    upload_data['title'] = request_title()
    upload_data['description'] = click.prompt('Descrição', type=str)
    upload_data['keywords'] = click.prompt('Palavras-chave', type=str)

    click.echo(f'{CATEGORY_OPTIONS}')
    upload_data['category'] = request_category()

    click.echo(f'{PRIVACY_STATUS_OPTIONS}')
    upload_data['privacyStatus'] = request_privacy_status()

    return upload_data
