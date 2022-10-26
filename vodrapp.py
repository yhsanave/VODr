import os
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Header, Footer

import utils
from vod import VOD, ARGUMENTS_LIST as VOD_ARGS
from startgg import Tournament

class VODrApp(App):
    """Textual App for labeling VODs"""

    BINDINGS = [
        ('n','next_vod','Next VOD'),
        ('p','previous_vod','Previous VOD'),
        ('t','edit_tournament','Edit Tournament')
    ]

    currentVodIndex: reactive[int] = reactive(0)
    currentVod: reactive[VOD | None] = reactive(None)
    vods: list[VOD] = [] 

    def __init__(self, tournament: Tournament, vods: list[VOD]):
        self.tournament = tournament
        self.vods = vods
        super().__init__()

    def on_mount(self):
        self.title = 'VODr'

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_next_vod(self):
        if self.currentVodIndex < len(self.vods) - 1:
            self.currentVodIndex += 1

    def action_previous_vod(self):
        if self.currentVodIndex > 0:
            self.currentVodIndex -= 1

    def action_edit_tournament(self):
        pass

    def watch_currentVodIndex(self, new_index: int):
        try:
            self.currentVod = self.vods[new_index]
        except:
            pass

    def watch_currentVod(self, new_vod: VOD):
        try: 
            self.sub_title = f'{new_vod.filename} ({self.currentVodIndex+1}/{len(self.vods)})'
        except: 
            self.sub_title = ''

if __name__ == "__main__":
    utils.check_files()
    tournament = Tournament('TCR23')
    vods = [VOD(f) for f in utils.filter_videos(os.listdir(utils.VIDEOS_PATH))]
    app = VODrApp(tournament, vods)
    app.run()