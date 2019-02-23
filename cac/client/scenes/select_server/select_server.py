import curses
from typing import Optional

from cac.client.scenes.select_server.manual_connect_page import \
    ManualConnectForm
from cac.client.scenes.select_server.auto_discovery_page import \
    SelectAutoDiscoveryServer
from cac.client.engine.game_object import Scene
from cac.client.engine.events import EventPropagation
from cac.client.engine.curses_colour import get_colour_pair
from cac.client.engine.curses_text import render_text
from cac.client.engine.events_keyboard import KeyboardEvent
from cac.client.engine.layout import Size, Layers, Place, Margin, Vertical
from cac.client.game_objects.background import HypnoBackground
from cac.client.game_objects.uiframe import UiFrame
from cac.client.game_objects.label import Label


class ReplaceWithServerException(Exception):
    """
    Exception that is raised to exit the game and tell
    the main method to instead run the cac server.
    """
    pass


class SelectServerScene(Scene):

    def __init__(self, bg: Optional[HypnoBackground] = None):
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

        # gackground pattern
        self._bg = bg

        # ui frame
        self._ui = UiFrame()

        # help text
        self._help = Label("FOOOOOOO")


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
        return [self._bg, self._ui, self._shown_page, self._help]

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

        # set the help text based on which view is visible
        if self._shown_page == self._page_autodiscover:
            f3_text = "Connect manually   "
        else:
            f3_text = "Autodiscover server"
        self._help.text = f"  <F3>: {f3_text}           <F2>: Run server"
        
        # reposition the children
        Layers(
            Place(self._bg),
            Size(
                width=.75, height=.75,
                child = Layers(
                    Place(self._ui),
                    Margin(
                        margin=1, bottom=1,
                        child = Vertical(0,
                            Place(self._shown_page, min_width=80, min_height=24),
                            Place(self._help, min_width=60, min_height=1),
                        )
                    )
                )
            )
        ).applyParent(self)



    def render(self, win):
        win.erase()
        w, h = self.size
        text_format = get_colour_pair(0, 1, 0, 0, 0, 0)

        hx, hy = self._help.position
        hw, hh = self._help.size

        render_text(
            win, f"x:{hx} y:{hy} w:{hw} h:{hh}",
            5, 5, w-5, h-5,
            text_format=text_format,
        )


    def start_server(self):
        raise ReplaceWithServerException()
