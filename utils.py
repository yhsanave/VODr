import re, os

# Constants
VIDEO_FORMAT_REGEX = r'.*\.(?:MOV|MPEG-1|MPEG-2|MPEG4|MP4|MPG|AVI|WMV|MPEGPS|FLV|3GPP?|WEBM)$'
TOURNAMENT_LINK_REGEX = r'https?:\/\/(www\.)?start\.gg(?:\/tournament)?\/(.*)\/?'

DEFAULT_TITLE_TEMPLATE = '%TournamentShort %Event %RoundShort - %P1 (%P1Chars) vs %P2 (%P2Chars)'
DEFAULT_DESCRIPTION_TEMPLATE = '%P1 vs %P2 at %Tournament in %Round\nBracket: %Link'

# Errors
class InvalidLinkError(Exception):
    pass

class TournamentNotFoundError(Exception):
    pass

# Functions
def parse_link(link: str):
        m = re.match(TOURNAMENT_LINK_REGEX, link)
        if m:
            return m.group(1)
        else:
            raise InvalidLinkError('The link you entered is not a valid start.gg tournament link.')

def filter_videos(files: list[str]):
    pattern = re.compile(VIDEO_FORMAT_REGEX, re.I)
    return [*filter(pattern.match, files)]

def open_video(path: str):
    if os.path.exists(path):
        os.startfile(path)
    else:
        print(f'Video not found: {path}')

def check_dirs():
    # Create directories if they don't already exist
    if not os.path.exists('./upload'): 
        os.mkdir('./upload')
    if not os.path.exists('./done'): 
        os.mkdir('./done')
    if not os.path.exists('./auth'): 
        os.mkdir('./auth')
    if not os.path.exists('./templates'):
        os.mkdir('./templates')

    # Check for templates files
    if not os.path.exists('./templates/title.txt'):
        with open('./templates/title.txt', 'w') as f:
            f.write(DEFAULT_TITLE_TEMPLATE)
            print('Using default title template. Set a custom template in config/title.txt. See the README for syntax help.')
    if not os.path.exists('./templates/description.txt'):
        with open('./templates/description.txt', 'w') as f:
            f.write(DEFAULT_DESCRIPTION_TEMPLATE)
            print('Using default description template. Set a custom template in config/description.txt. See the README for syntax help.')

    # Check for auth files and alert user and exit the program if they are missing
    missingAuth = False
    if not os.path.exists('./auth/startggtoken.txt'):
        with open('./auth/startggtoken.txt', 'x'):
            print('Start.gg API token not found. Please paste your start.gg into auth/startggtoken.txt')
            missingAuth = True
    if not os.path.exists('./auth/client_secrets.json'):
        print('Youtube API client info not found. Please put client_secrets.json into the /auth directory')
        missingAuth = True
    
    # if missingAuth: exit()