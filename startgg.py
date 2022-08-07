# Start.gg API Wrapper

import requests
from math import ceil
from functools import cache
from rich import print
from rich.tree import Tree
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
from prompt_toolkit.completion import FuzzyWordCompleter

import utils

utils.check_files()

API_URL = r'https://api.start.gg/gql/alpha'
CHARACTER_API_URL = r'https://api.smash.gg/characters?videogameId='

try:
    with open(utils.API_TOKEN_PATH, 'r') as f:
        apiToken = f.read()
    if not apiToken:
        raise
except:
    open('token.txt', 'w').close()
    print('[red]No start.gg api key found. Paste your api key into token.txt')
    utils.leave()

class CharImage:
    id: int
    width: int
    height: int
    type: str
    url: str

    def __init__(self, image) -> None:
        self.id = image['id']
        self.width = image['width']
        self.height = image['height']
        self.type = image['type']
        self.url = image['url']


class Character:
    id: int
    name: str
    images: list[CharImage]

    def __init__(self, char) -> None:
        self.id = char['id']
        self.name = char['name']
        self.images = [CharImage(i) for i in char['images']]

    def __repr__(self) -> str:
        return self.name


class VideoGame:
    id: int
    name: str
    characters: list[Character]
    characterCompleter: FuzzyWordCompleter

    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name
        self.characters = self.get_game_characters()
        self.characterCompleter = FuzzyWordCompleter(
            words=[c.name for c in self.characters])

    def __repr__(self) -> str:
        return self.name

    @cache
    def get_game_characters(self) -> list[Character]:
        url = f'{CHARACTER_API_URL}{self.id}'
        res = requests.get(url).json()['entities']['character']
        characters = [Character(c) for c in res]
        return characters

    @cache
    def get_character(self, id: int = None, name: str = '') -> Character:
        char = next((c for c in self.characters if c.id ==
                    id or c.name.lower() == name.lower()), None)
        if not char:
            raise utils.CharacterNotFoundError(
                f'Character not found: {id or ""}{name or ""}')
        return char


class Player:
    id: int
    name: str
    characters: list[Character]
    videoGame: VideoGame

    def __init__(self, slots, games, videoGame: VideoGame) -> None:
        self.id = slots['entrant']['id']
        self.name = slots['entrant']['name']
        self.videoGame = videoGame

        if games:
            selections = []
            for game in games:
                if game['selections']:
                    for selection in game['selections']:
                        char = {'id': selection['entrant']['id'],
                                'value': selection['selectionValue']}
                        if char not in selections:
                            selections.append(char)

            self.characters = [videoGame.get_character(
                id=s['value']) for s in selections if s['id'] == self.id]
        else:
            self.characters = []

    def __repr__(self) -> str:
        return f'{self.name}{f" {self.print_chars()}" if self.characters else ""}'

    def print_chars(self) -> str:
        return f'({", ".join([c.name for c in self.characters])})' if self.characters else ''

    def try_set_chars(self, chars: str) -> None:
        try:
            self.characters = [self.videoGame.get_character(
                name=c.strip()) for c in chars.split(';')]
        except utils.CharacterNotFoundError as err:
            print(err)


class Set:
    round: str
    roundShort: str
    videoGame: VideoGame
    players: list[Player]

    p1: int = 0

    def __init__(self, data, game: VideoGame) -> None:
        self.videoGame = game
        self.round = data['fullRoundText']
        self.roundShort = self.shorten_round(self.round)
        self.players = [Player(s, data['games'], self.videoGame)
                        for s in data['slots']]

    def __repr__(self) -> str:
        return f'[red]{self.players[self.p1]}[/red] vs [blue]{self.players[1 - self.p1]}[/blue]'

    def __rich_repr__(self):
        yield f'[red]{self.players[self.p1]}[/red] vs [blue]{self.players[1 - self.p1]}[/blue]'

    def __rich_console__(self, console, options):
        yield f'[red]{self.players[self.p1]}[/red] vs [blue]{self.players[1 - self.p1]}[/blue]'

    def shorten_round(self, round: str) -> str:
        return round.replace(' ', '').replace('-', '').replace('Winners', 'W').replace('Losers', 'L').replace('Quarter', 'Q').replace('Semi', 'S').replace('Grand', 'G').replace('Final', 'F').replace('Round', 'R').replace('Reset', ' Reset')


class Phase:
    name: str
    numSeeds: int
    numSets: int
    game: VideoGame
    sets: list[Set]

    setName: str = ''

    QUERY = '''query PhaseSets($id: ID!, $page: Int!) {
                phase(id: $id) {
                    sets(page: $page, perPage: 40, sortType: CALL_ORDER) {
                        nodes {
                            event {
                                videogame {
                                    id
                                    name
                                }
                            }
                            fullRoundText
                            games {
                                selections {
                                    entrant {
                                        id
                                    }
                                    selectionValue
                                }
                            }
                            slots {
                                entrant {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            }'''

    def __init__(self, data, game: VideoGame) -> None:
        self.id = data['id']
        self.name = data['name']
        self.numSeeds = data['numSeeds']
        self.numSets = data['sets']['pageInfo']['total']
        self.game = game
        self.sets = self.get_sets()

    def __repr__(self) -> str:
        return f'{self.name} ({self.numSeeds} entrants) ({self.numSets} sets)'

    def __rich_console__(self, console, options):
        yield f'{self.name} ({self.numSeeds} entrants) ({self.numSets} sets)'

    @cache
    def get_sets(self) -> list[Set]:
        sets = []

        for page in track(range(ceil(self.numSets / 40)), description='[white]Getting sets...', transient=True):
            data = requests.post(API_URL, headers={'Authorization': f'Bearer {apiToken}'}, json={
                'query': Phase.QUERY, 'variables': {'id': self.id, 'page': page+1}}).json()['data']['phase']['sets']
            sets.extend([Set(s, self.game) for s in data['nodes']])

        return [*reversed(sets)]


class Event:
    name: str
    game: VideoGame
    phases: list[Phase]

    setName: str = ''

    def __init__(self, data) -> None:
        self.name = data['name']
        self.game = VideoGame(data['videogame']['id'],
                              data['videogame']['name'])
        self.phases = [Phase(p, self.game) for p in data['phases']]

    def __repr__(self) -> str:
        return f'{self.name} - {self.game} ({len(self.phases)} phases)'

    def __rich_console__(self, console, options):
        yield f'{self.name} - {self.game} ({len(self.phases)} phases)'


class Tournament:
    name: str
    slug: str
    shortSlug: str
    url: str
    events: list[Event]

    tree: Tree
    shortName: str

    QUERY = '''query Tournament($slug: String!) {
                    tournament(slug: $slug){
                        name
                        slug
                        shortSlug
                        url
                        events {
                            name
                            videogame {
                                id
                                name
                            }
                            phases {
                              id
                              name
                              numSeeds
                              sets {
                                pageInfo {
                                    total
                                }
                              }
                            }
                        }
                    }
                }'''

    def __init__(self, slug: str) -> None:
        data = self.query(slug)
        self.name = data['name']
        self.slug = data['slug']
        self.shortSlug = data['shortSlug']
        self.url = data["url"]
        self.events = [Event(e) for e in data['events']]
        self.shortName = self.shortSlug or None
        self.build_tree()

    def __repr__(self) -> str:
        return self.name

    def __rich_console__(self, console, options):
        yield self.name

    @cache
    def query(self, slug: str) -> dict:
        print('[white]Getting tournament data... ', end='')
        data = requests.post(API_URL, headers={'Authorization': f'Bearer {apiToken}'}, json={
                             'query': Tournament.QUERY, 'variables': {'slug': slug}}).json()['data']['tournament']
        if not data:
            raise utils.TournamentNotFoundError('Tournament not found')
        print('[green]Done!')
        return data

    def build_tree(self):
        tournamentTreeFull = Tree(self.name)
        tournamentTreeSmall = Tree(self.name, hide_root=True)
        for ei, e in enumerate(self.events):
            eventTreeFull = tournamentTreeFull.add(f'[green]\[{ei}.x.x][/green] {e}')
            eventTreeSmall = tournamentTreeSmall.add(f'[green]\[{ei}.x][/green] {e}')
            for pi, p in enumerate(e.phases):
                phaseTreeFull = eventTreeFull.add(f'[green]\[{ei}.{pi}.x][/green] {p}')
                eventTreeSmall.add(f'[green]\[{ei}.{pi}][/green] {p}')

                rounds = {}
                for si, s in enumerate(p.sets):
                    if s.round not in rounds:
                        rounds[s.round] = []

                    rounds[s.round].append((si, s))

                for r in rounds.keys():
                    roundTree = phaseTreeFull.add(r)
                    for si, s in rounds[r]:
                        roundTree.add(f'[green]\[{ei}.{pi}.{si}][/green] {s}')

        self.tree = tournamentTreeFull
        self.treeSmall = tournamentTreeSmall

    def parse_index(self, id: str):
        try:
            i = [i for i in map(int, id.split('.'))]
            yield self.events[i[0]]
            yield self.events[i[0]].phases[i[1]]
            yield self.events[i[0]].phases[i[1]].sets[i[2]]
        except:
            print(f'[red]:warning: Invalid set index: {id}[/red]')
            return None

    def summary_table(self):
        grid = Table.grid(padding=(0, 1), expand=False)
        grid.add_column(justify='right')
        grid.add_column()

        grid.add_row('[green]Name[/]:', self.name)
        grid.add_row('[green]Short Name[/]:', self.shortName)
        grid.add_row('[green]Link[/]:', f'https://start.gg/{self.url}')
        grid.add_row('[green]Events[/]:', self.treeSmall)

        return Panel(grid, title='Tournament', expand=False)


if __name__ == '__main__':
    tournament = Tournament('LoL60')
    print(tournament.tree)
