import curses

from cac.client.scenes.select_server.manual_connect_page import \
    ManualConnectForm
from cac.client.scenes.select_server.auto_discovery_page import \
    SelectAutoDiscoveryServer
from cac.client.engine.game_object import Scene
from cac.client.engine.events import EventPropagation
from cac.client.engine.curses_colour import get_colour_pair
from cac.client.engine.events_keyboard import KeyboardEvent
from cac.client.engine.curses_text import render_text


class ReplaceWithServerException(Exception):
    """
    Exception that is raised to exit the game and tell
    the main method to instead run the cac server.
    """
    pass


class SelectServerScene(Scene):

    def __init__(self):
        super().__init__()

        # game
        self._game = None

        # manual connection dialog
        self._page_manual_connection = ManualConnectForm()

        # autodiscovery dialog
        self._page_autodiscover = SelectAutoDiscoveryServer()
        self._discovery_enabled = False

        # which page is shown
        self._shown_page = self._page_autodiscover

    def start_scene(self, game):
        self._game = game
        try:
            self._page_autodiscover.start_discovery()
            self._discovery_enabled = True
        except Exception:
            pass

    def stop_scene(self):
        if self._discovery_enabled:
            self._page_autodiscover.stop_discovery()
            self._discovery_enabled = False

    def get_child_objects(self):
        return [self._shown_page]

    def process_event(self, event):

        # keyboard shortcuts
        if isinstance(event, KeyboardEvent):
            if event.key_code == curses.KEY_F2:
                self.start_server()
            elif event.key_code == curses.KEY_F3:
                if self._shown_page == self._page_autodiscover:
                    self._shown_page = self._page_manual_connection
                else:
                    self._shown_page = self._page_autodiscover

        return EventPropagation.propagate_forward(self._shown_page)

    def update(self, delta_time):

        # reposition the children
        w, h = self.size
        self._shown_page.position = 0, 0
        self._shown_page.size = w, h - 3

    def render(self, win):
        w, h = self.size
        win.erase()

        # render the "Help section"
        if self._shown_page == self._page_autodiscover:
            f3_text = "Connect manually   "
        else:
            f3_text = "Autodiscover server"

        white_text = get_colour_pair(1, 1, 1, 0, 0, 0)
        render_text(
            win, f"  <F3>: {f3_text}           <F2>: Run server",
            0, h - 2, w, 1,
            text_format=white_text,
        )

    def start_server(self):
        raise ReplaceWithServerException()
