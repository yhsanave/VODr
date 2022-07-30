# Start.gg API Wrapper
from dataclasses import dataclass
import requests
import utils
from functools import cache

API_URL = r'https://api.start.gg/gql/alpha'
CHARACTER_API_URL = r'https://api.smash.gg/characters?videogameId='

with open('./auth/startggtoken.txt', 'r') as f:
    apiToken = f.read()

# Character Data
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

    def __init__(self, char):
        self.id = char['id']
        self.name = char['name']
        self.images = [CharImage(i) for i in char['images']]

    def __repr__(self) -> str:
        return self.name

class VideoGame:
    id: int
    name: str
    characters: list[Character]

    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name
        self.characters = self.get_game_characters(id)

    def __repr__(self) -> str:
        return self.name

    @cache    
    def get_game_characters(self, gameId: int) -> list[Character]:
        url = f'{CHARACTER_API_URL}{gameId}'
        res = requests.get(url).json()['entities']['character']
        characters = [Character(c) for c in res]
        return characters

    @cache
    def get_character(self, id: int):
        return next((c for c in self.characters if c.id == id), None)

# Tournament Data
@dataclass
class Player:
    id: int
    name: str
    characters: list[Character]

    def __init__(self, slots, games, videoGame: VideoGame) -> None:
        self.id = slots['entrant']['id']
        self.name = slots['entrant']['name']

        if games:
            selections = []
            for game in games:
                for selection in game['selections']:
                    char = {'id': selection['entrant']['id'], 'value': selection['selectionValue']}
                    if char not in selections:
                        selections.append(char)

            self.characters = [videoGame.get_character(s['value']) for s in selections if s['id'] == self.id]
        else:
            self.characters = []

    def __repr__(self) -> str:
        return f'{self.name}{self.print_chars()}'

    def print_chars(self):
        return f' ({", ".join([c.name for c in self.characters])})' if self.characters else ''


class Set:
    round: str
    roundShort: str
    videoGame: VideoGame
    players: list[Player]

    p1: int = 0

    def __init__(self, data) -> None:
        self.videoGame = VideoGame(data['event']['videogame']['id'], data['event']['videogame']['name'])
        self.round = data['fullRoundText']
        self.roundShort = self.shorten_round(self.round)
        self.players = [Player(s, data['games'], self.videoGame) for s in data['slots']]

    def __repr__(self) -> str:
        return f'{self.roundShort} - {self.players[self.p1]} vs {self.players[1 - self.p1]}'

    def shorten_round(self, round: str) -> str:
        return round.replace(' ', '').replace('-', '').replace('Winners', 'W').replace('Losers', 'L').replace('Quarter', 'Q').replace('Semi', 'S').replace('Final', 'F').replace('Round', 'R')

class SetPage:
    setCount: int
    pages: int
    page: int
    perPage: int

    sets: list[Set]

    def __init__(self, data) -> None:
        self.setCount = data['pageInfo']['total']
        self.pages = data['pageInfo']['totalPages']
        self.page = data['pageInfo']['page']
        self.perPage = data['pageInfo']['perPage']

        self.sets = [Set(s) for s in data['nodes']]

    def __repr__(self) -> str:
        return f'Page {self.page} / {self.pages} ({self.setCount} sets total)'

class Phase:
    name: str
    numSeeds: int

    setName: str = ''

    QUERY = '''query PhaseSets($id: ID!, $page: Int!) {
                phase(id: $id) {
                    sets(page: $page, perPage: 10, sortType: CALL_ORDER) {
                        pageInfo{
                            total
                            totalPages
                            page
                            perPage
                        }
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

    def __init__(self, data) -> None:
        self.id = data['id']
        self.name = data['name']
        self.numSeeds = data['numSeeds']

    def __repr__(self) -> str:
        return f'{self.name} ({self.numSeeds} entrants)'

    @cache
    def get_sets(self, page: int):
        data = requests.post(API_URL, headers={'Authorization': f'Bearer {apiToken}'}, json={'query': Phase.QUERY, 'variables': {'id': self.id, 'page': page}}).json()['data']['phase']['sets']
        return SetPage(data)

class Event:
    name: str
    game: VideoGame
    phases: list[Phase]

    setName: str = ''

    def __init__(self, data) -> None:
        self.name = data['name']
        self.game = VideoGame(data['videogame']['id'], data['videogame']['name'])
        self.phases = [Phase(p) for p in data['phases']]

    def __repr__(self) -> str:
        return f'{self.name} - {self.game} ({len(self.phases)} phases)'

class Tournament:
    name: str
    slug: str
    shortSlug: str
    url: str
    events: list[Event]

    setName: str = ''
    shortName: str = ''

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

    def __repr__(self) -> str:
        return self.name

    @cache
    def query(self, slug: str):
        data = requests.post(API_URL, headers={'Authorization': f'Bearer {apiToken}'}, json={'query': Tournament.QUERY, 'variables': {'slug': slug}}).json()['data']['tournament']
        if not data:
            raise utils.TournamentNotFoundError('Tournament not found')
        return data