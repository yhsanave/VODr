import json
import re
import os
from functools import reduce

VIDEO_FORMAT_REGEX = r'.*\.(?:MOV|MPEG-1|MPEG-2|MPEG4|MP4|MPG|AVI|WMV|MPEGPS|FLV|WEBM)$'
TOURNAMENT_LINK_REGEX = r'https?:\/\/(?:www\.)?start\.gg(?:\/tournament)?\/(?:(?:(.+?)(?=\/))|(.+))'

DEFAULT_TITLE_TEMPLATE = '%TournamentShort %Event %Phase %RoundShort - %P1 %P1Chars vs %P2 %P2Chars'
DEFAULT_DESCRIPTION_TEMPLATE = '%P1 vs %P2 playing %Game at %Tournament in %Round\nBracket: %Link'

VIDEOS_PATH = 'videos'
TEMPLATES_PATH = 'templates'
API_TOKEN_PATH = 'token.txt'


class InvalidLinkError(Exception):
    pass


class TournamentNotFoundError(Exception):
    pass


class CharacterNotFoundError(Exception):
    pass


def parse_link(link: str) -> str:
    m = re.match(TOURNAMENT_LINK_REGEX, link)
    if m:
        return m.group(1) or m.group(2)
    else:
        raise InvalidLinkError(
            'The link you entered is not a valid start.gg tournament link.')


def filter_videos(files: list[str]) -> list[str]:
    pattern = re.compile(VIDEO_FORMAT_REGEX, re.I)
    return [*filter(pattern.match, files)]


def file_name_safe(name: str) -> str:
    return name.replace('<', '').replace('>', '').replace(':', '').replace('"', '').replace('/', '%2F').replace('\\', '').replace('|', '').replace('?', '').replace('*', '')


def export_code(vods) -> str:
    filtered = filter(lambda v: v.processed, vods)
    if filtered:
        dicts = map(lambda v: v.export_dict(), filtered)
        dict = reduce(lambda a, b: a | b, dicts)
        return json.dumps(dict)
    else:
        return ''

def leave() -> None:
    input('Press [Enter] to exit...')
    exit()


def check_files() -> bool:
    # Create directories if they don't already exist
    if not os.path.exists(VIDEOS_PATH):
        os.mkdir(VIDEOS_PATH)
    if not os.path.exists(TEMPLATES_PATH):
        os.mkdir(TEMPLATES_PATH)

    # Check for templates files
    if not os.path.exists(os.path.join(TEMPLATES_PATH, 'title.txt')):
        with open(os.path.join(TEMPLATES_PATH, 'title.txt'), 'w') as f:
            f.write(DEFAULT_TITLE_TEMPLATE)
            print('Using default title template. Set a custom template in templates/title.txt. See the README for syntax help.')
    if not os.path.exists(os.path.join(TEMPLATES_PATH, 'description.txt')):
        with open(os.path.join(TEMPLATES_PATH, 'description.txt'), 'w') as f:
            f.write(DEFAULT_DESCRIPTION_TEMPLATE)
            print('Using default description template. Set a custom template in templates/description.txt. See the README for syntax help.')

    # Check for startgg token
    if not os.path.exists(API_TOKEN_PATH):
        with open(API_TOKEN_PATH, 'x'):
            print(
                'Start.gg API token not found. Please paste your start.gg token into token.txt')
            return False

    return True
