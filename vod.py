import os
import startgg
import utils
import templates
from rich import print
from rich.console import Console, ConsoleOptions
from rich.panel import Panel
from rich.table import Table

ARGUMENTS_LIST = ['Tournament', 'Tournament Short', 'Link', 'Event', 'Phase', 'Round',
                  'Round Short', 'Game', 'Player 1', 'Player 2', 'Player 1 Characters', 'Player 2 Characters']


class VOD:
    filename: str
    path: str

    tournament: startgg.Tournament = None
    event: startgg.Event = None
    phase: startgg.Phase = None
    set: startgg.Set = None

    templateArgs: templates.TemplateArgs = None
    title: str = ''
    description: str = ''

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.path = os.path.join(utils.VIDEOS_PATH, filename)

    def __rich_repr__(self):
        yield 'Tournament', self.tournament
        yield 'Event', self.event
        yield 'Phase', self.phase
        yield 'Set', self.set
        yield 'Title', self.title
        yield 'Description', self.description

    def __rich_console__(self, console: Console, options: ConsoleOptions):
        yield 'Tournament', self.tournament
        yield 'Event', self.event
        yield 'Phase', self.phase
        yield 'Set', self.set
        yield 'Title', self.title
        yield 'Description', self.description

    def summary_table(self):
        grid = Table.grid(padding=(0, 1), expand=False)
        grid.add_column(justify='right')
        grid.add_column()

        grid.add_row('[green]Tournament[/green]: ',
                     f'[red]{self.tournament.name}[/] ([blue]{self.tournament.shortName}[/])')
        grid.add_row('[green]Event[/green]: ',
                     f'[red]{self.event.name}[/] - [blue]{self.event.game}')
        grid.add_row('[green]Phase[/green]: ', f'[red]{self.phase.name}')
        grid.add_row('[green]Set[/green]: ', f'{self.set}')
        grid.add_row('[green]Title[/green]: ', f'[yellow]{self.title}')
        grid.add_row('[green]Description[/green]: ',
                     f'[yellow]{self.description}')

        return Panel(grid, title=self.filename, expand=False)

    def edit_table(self):
        grid = Table.grid(padding=(0, 1), expand=False)
        grid.add_column(justify='right')
        grid.add_column()

        grid.add_row('Tournament [green]\[1][/]:',
                     self.templateArgs.tournamentName)
        grid.add_row('Tournament Short [green]\[2][/]:',
                     self.templateArgs.tournamentShort)
        grid.add_row('Link [green]\[3][/]:', self.templateArgs.tournamentLink)
        grid.add_row('Event [green]\[4][/]:', self.templateArgs.eventName)
        grid.add_row('Phase [green]\[5][/]:', self.templateArgs.phaseName)
        grid.add_row('Round [green]\[6][/]:', self.templateArgs.roundFull)
        grid.add_row('Round Short [green]\[7][/]:',
                     self.templateArgs.roundShort)
        grid.add_row('Game [green]\[8][/]:', self.templateArgs.game)
        grid.add_row('Player 1 [green]\[9][/]:', self.templateArgs.player1)
        grid.add_row('Player 2 [green]\[10][/]:', self.templateArgs.player2)
        grid.add_row(
            'Player 1 Characters [green]\[11][/]:', self.templateArgs.player1Chars)
        grid.add_row(
            'Player 2 Characters [green]\[12][/]:', self.templateArgs.player2Chars)

        return Panel(grid, title='Edit Values', expand=False)

    def process_template(self) -> None:
        self.title = templates.parse(
            templates.TITLE_TEMPLATE, self.templateArgs)
        self.description = templates.parse(
            templates.DESCRIPTION_TEMPLATE, self.templateArgs)

    def generate_template_args(self):
        self.templateArgs = templates.TemplateArgs(
            self.tournament, self.event, self.phase, self.set)
        self.process_template()

    def set_arg(self, index: int, value: str):
        args = [None for _ in range(len(ARGUMENTS_LIST)+1)]
        args[index] = value
        self.set_template_args(*args)

    def set_template_args(self,
                          templateArgs: templates.TemplateArgs = None,
                          tournamentName: str = None,
                          tournamentShort: str = None,
                          tournamentLink: str = None,
                          eventName: str = None,
                          phaseName: str = None,
                          roundFull: str = None,
                          roundShort: str = None,
                          game: str = None,
                          player1: str = None,
                          player2: str = None,
                          player1Chars: str = None,
                          player2Chars: str = None) -> None:
        if templateArgs:
            self.templateArgs = templateArgs
        else:
            self.templateArgs.tournamentName = tournamentName or self.templateArgs.tournamentName
            self.templateArgs.tournamentShort = tournamentShort or self.templateArgs.tournamentShort
            self.templateArgs.tournamentLink = tournamentLink or self.templateArgs.tournamentLink
            self.templateArgs.eventName = eventName or self.templateArgs.eventName
            self.templateArgs.phaseName = phaseName or self.templateArgs.phaseName
            self.templateArgs.roundFull = roundFull or self.templateArgs.roundFull
            self.templateArgs.roundShort = roundShort or self.templateArgs.roundShort
            self.templateArgs.game = game or self.templateArgs.game
            self.templateArgs.player1 = player1 or self.templateArgs.player1
            self.templateArgs.player2 = player2 or self.templateArgs.player2
            self.templateArgs.player1Chars = player1Chars or self.templateArgs.player1Chars
            self.templateArgs.player2Chars = player2Chars or self.templateArgs.player2Chars

        self.process_template()

    def open_video(self) -> None:
        if os.path.exists(self.path):
            print(f'Opening Video: {self.filename}')
            os.startfile(self.path)
        else:
            print(f'Video not found: {self.path}')

    def export_dict(self):
        return {
            self.filename: {
                'title': self.title,
                'description': self.description
            }
        }


if __name__ == '__main__':
    from vod import VOD
    from startgg import Tournament
    v = VOD('test.mov')
    t = Tournament('LoL60')
    t.shortName = 'LoL60'
    v.tournament = t
    v.event = t.events[0]
    v.phase = t.events[0].phases[0]
    v.set = t.events[0].phases[0].sets[22]
    v.generate_template_args()
    from rich import print
    print(v.summary_table())
