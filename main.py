
from functools import reduce
import json
import os
from startgg import Tournament, Event, Phase, Set
import utils
from vod import VOD, ARGUMENTS_LIST as VOD_ARGS
from rich import print
from rich.prompt import Prompt, Confirm, IntPrompt
from prompt_toolkit import prompt
import pyperclip


def main() -> None:
    if not utils.check_files():
        utils.leave()

    # Get videos from ./videos
    vods = [VOD(f) for f in utils.filter_videos(os.listdir(utils.VIDEOS_PATH))]
    if not vods:
        print('No videos found, please place videos in /videos.')
        utils.leave()

    # Get startgg tournament
    tournament: Tournament = None
    while not tournament:
        link = Prompt.ask('Enter start.gg link')
        try:
            slug = utils.parse_link(link)
            tournament = Tournament(slug)
            tournament.shortName = Prompt.ask(
                'Enter abbreviated tournament name')
        except (utils.InvalidLinkError):
            print(f'[red]Invalid link:[/red] {link}')
        except (utils.TournamentNotFoundError):
            print(f'[red]Tournament not found:[/red] {slug}')

    # Get data for each vod
    for vod in vods:
        print()
        print(tournament.tree)
        print()
        vod.open_video()

        skip = False
        confirmSet = False
        while not confirmSet:
            event: Event = None
            phase: Phase = None
            set: Set = None
            # Select the set
            while not set:
                setId = Prompt.ask(
                    'Enter [green]\[Set ID][/green] (Enter [green]V[/] to reopen video, [green]X[/] to skip video)')

                if setId.lower() == 'v':
                    vod.open_video()
                    continue

                if setId.lower() == 'x':
                    skip = True
                    break

                try:
                    event, phase, set = tournament.parse_index(setId)
                except:
                    pass

            if skip:
                break

            # Confirm the selection
            confirmSet = Confirm.ask(
                f'Selected {set.roundShort} - {set}. Is this correct?')

        if skip:
            print(f'[yellow] Skipping video: {vod.filename}')
            continue

        # Check player order
        if not Confirm.ask('Are the players in the correct order?'):
            set.p1 = 1

        # Check for missing characters and prompt to manually add them
        for player in set.players:
            if not player.characters:
                if Confirm.ask(f'No character data found for {player.name}. Manually enter characers?'):
                    chars = []
                    while not chars:
                        charInput = prompt(
                            f'Enter characters played by {player.name} (Separated by semi-colons): ', completer=set.videoGame.characterCompleter)
                        try:
                            chars = [set.videoGame.get_character(
                                name=c.strip()) for c in charInput.split(';')]
                        except:
                            chars = None
                    player.characters = chars

        # Insert data into the vod and process the template with it
        vod.tournament = tournament
        vod.event = event
        vod.phase = phase
        vod.set = set
        vod.generate_template_args()

        while True:
            print()
            print(vod.summary_table())
            print()
            if not Confirm.ask('Is this information correct?'):
                while True:
                    print()
                    print(vod.edit_table())
                    print()
                    index = IntPrompt.ask('Which value is incorrect? (Enter [green]0[/] to exit)', default=0,
                                          show_choices=False, show_default=False, choices=[str(i) for i in range(len(VOD_ARGS)+1)])
                    if index == 0:
                        break
                    resp = Prompt.ask(
                        f'Enter new value for {VOD_ARGS[index-1]}')
                    vod.set_arg(index, resp)
            else:
                break

    exportVods = reduce(lambda a, b: a | b, map(
        lambda v: v.export_dict(), vods))
    pyperclip.copy(json.dumps(exportVods))
    print('[green]Export code copied to clipboard')
    utils.leave()

if __name__ == "__main__":
    main()
