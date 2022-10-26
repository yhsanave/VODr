from textual.app import ComposeResult
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Header, Footer

class VODScreen(Screen):
    BINDINGS = [
        ('s','select_set','Select Set')
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield VODForm()
        yield Footer()

class VODForm(Widget):
    pass