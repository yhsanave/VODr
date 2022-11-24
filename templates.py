import startgg, re
from utils import check_files

check_files()

with open('./templates/title.txt', 'r') as template:
    TITLE_TEMPLATE = template.read()

with open('./templates/description.txt', 'r') as template:
    DESCRIPTION_TEMPLATE = template.read()

TOURNAMENT_NAME = r'%Tournament'
TOURNAMENT_SHORT = r'%TournamentShort'
TOURNAMENT_LINK = r'%Link'

EVENT_NAME = r'%Event'

PHASE_NAME = r'%Phase'

ROUND_FULL = r'%RoundFull'
ROUND_SHORT = r'%RoundShort'

GAME = r'%Game'

PLAYER_1 = r'%P1'
PLAYER_2 = r'%P2'
PLAYER_1_CHARS = r'%P1Chars'
PLAYER_2_CHARS = r'%P2Chars'

COLLAPSE_WS_REGEX = re.compile(r' +')

class TemplateArgs:
    tournamentName: str = 'Default Tournament'
    tournamentShort: str = 'DT#0'
    tournamentLink: str = 'https://start.gg'
    eventName: str = 'Nils'
    phaseName: str = 'Pools'
    roundFull: str = 'Winners Round 0'
    roundShort: str = 'WR0'
    game: str = 'Super Smash Brothers Ultimate'
    player1: str = 'Yhsanave'
    player2: str = 'Not Yhsanave'
    player1Chars: str = '(Jigglypuff)'
    player2Chars: str = '(Sonic, Yoshi, Steve)'

    def __init__(self, tournament: startgg.Tournament, event: startgg.Event, phase: startgg.Phase, set: startgg.Set) -> None:
        self.tournamentName = tournament.name
        self.tournamentShort = tournament.shortName
        self.tournamentLink = f'https://start.gg{tournament.url}'
        self.eventName = event.name
        self.phaseName = phase.name
        self.roundFull = set.round
        self.roundShort = set.roundShort
        self.game = event.game.name
        self.player1 = set.players[set.p1].name
        self.player2 = set.players[1-set.p1].name
        self.player1Chars = set.players[set.p1].print_chars()
        self.player2Chars = set.players[1-set.p1].print_chars()


def parse(template: str, args: TemplateArgs) -> str:
    return COLLAPSE_WS_REGEX.sub(' ', template.replace(TOURNAMENT_SHORT, args.tournamentShort).replace(TOURNAMENT_NAME, args.tournamentName).replace(TOURNAMENT_SHORT, args.tournamentShort).replace(TOURNAMENT_LINK, args.tournamentLink).replace(EVENT_NAME, args.eventName).replace(PHASE_NAME, args.phaseName).replace(GAME, args.game).replace(ROUND_FULL, args.roundFull).replace(ROUND_SHORT, args.roundShort).replace(PLAYER_1_CHARS, args.player1Chars).replace(PLAYER_2_CHARS, args.player2Chars).replace(PLAYER_1, args.player1).replace(PLAYER_2, args.player2))
