import sys

from utils.util import is_blank
from pytube.exceptions import VideoUnavailable, RegexMatchError
from pytube import YouTube as YouTubePY

INVALID_CHARS = '/\:*<>|"'
CATEGORIES = (1, 2, 10, 15, 17, 19, 20, 22,
              23, 24, 25, 26, 27, 28, 29)
PRIVACY_STATUSES = ('public', 'private', 'unlisted')


def validate_ranges(ctx, param, ranges):
    ranges = ranges[0].split(',') if isinstance(ranges, tuple) else ranges.split(',')

    ranges = range_is_int(ranges)
    range_is_pos(ranges)
    range_is_complete(ranges)
    range_exists(ranges)

    return ranges


def range_exists(ranges):
    count = 0
    while (count <= len(ranges)-1):
        if count % 2 == 0:
            if ranges[count] > ranges[count + 1]:
                sys.exit(
                    f'Erro: tempo de início "{ranges[count]}" do corte não pode ser maior que o tempo final "{ranges[count + 1]}".')
        count += 2


def range_is_pos(ranges):
    for n in ranges:
        if n < 0:
            sys.exit(f'Erro: tempo de início e fim precisa ser um número positivo.')


def range_is_int(ranges):
    try:
        ranges = [int(r) for r in ranges if isinstance(r, str)]
    except:
        sys.exit(f'Erro: o tempo de início e fim precisa ser um número inteiro.')

    return ranges


def range_is_complete(ranges):
    if len(ranges) % 2 != 0:
        sys.exit(f'Erro: o par início-fim do range não está completo: "{ranges}"')


def validate_url(ctx, param, url):
    try:
        video = YouTubePY(url)
        del video
    except VideoUnavailable:
        sys.exit(f'Erro: url "{url}" não disponível.')
    except RegexMatchError:
        sys.exit(f'Erro: url "{url}" não disponível.')

    return url


def validate_name(ctx, param, name):
    if name:
        for char in name:
            if char in INVALID_CHARS or is_blank(char) == True:
                sys.exit(
                    f'Erro: nome informado "{name}" está vazio ou contém um ou mais caracteres inválidos.')
    else:
        return ' '

    return str(name)


def validate_highest(highest):
    return highest if highest == True or highest == False else \
        sys.exit(f'Erro: informação "{highest}" deve ser true ou false.')


######################################### CLI UPLOAD  #########################################


def validate_title(title):
    return title if is_blank(title) != True else None


def validate_category(category):
    return category if category in CATEGORIES else None


def validate_privacy_status(privacy_status):
    return privacy_status if privacy_status in PRIVACY_STATUSES else None
