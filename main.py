import os, re, requests
from dataclasses import dataclass
import startgg, templates, utils


class VOD:
    path: str
    set: startgg.Set
    title: str
    description: str
    player1: str
    player1Chars: list[str]
    player2: str
    player2Chars: list[str]

    def __init__(self, path: str, set: startgg.Set, templateArgs: templates.TemplateArgs) -> None:
        self.path = f'./upload/{path}'
        self.set = set

def main():
    utils.check_dirs()

    # Get videos from ./import
    videos = utils.filter_videos(os.listdir('./upload'))
    if not videos:
        print('No videos found, please place videos to upload in ./upload')
        exit()

    # Get startgg tournament
    tournament: startgg.Tournament = None
    while not tournament:
        link = input('Enter start.gg link: ')
        try:
            slug = utils.parse_link(link)
            tournament = startgg.Tournament(slug)
        except (utils.InvalidLinkError):
            print('Invalid Link')
        except (utils.TournamentNotFoundError):
            print('Tournament not found')

if __name__ == "__main__":
    main()