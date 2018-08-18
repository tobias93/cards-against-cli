import curses

from cac.client.engine.game_object import GameObject
from cac.client.engine.curses_text import render_text
from cac.client.engine.curses_colour import get_colour_pair
from cac.client.engine.events import EventPropagation
from cac.client.engine.events_keyboard import KeyboardEvent
from cac.client.scenes.select_server.text_box import TextBox


class ManualConnectForm(GameObject):

    def __init__(self):
        super().__init__()
        self._text_box_address = TextBox()
        self._text_box_address.text = "localhost"
        self._text_box_port = TextBox()
        self._text_box_port.text = "9852"
        self._focused_child = 0

    def get_child_objects(self):
        return [
            self._text_box_address,
            self._text_box_port,
        ]

    def process_event(self, event):

        if isinstance(event, KeyboardEvent):
            nr_childs = len(self.get_child_objects())
            focus_next_keys = [curses.KEY_DOWN, ord('\t')]
            focus_prev_keys = [curses.KEY_UP]
            if event.key_code in focus_next_keys:
                self._focused_child = (self._focused_child + 1) % nr_childs
            elif event.key_code in focus_prev_keys:
                self._focused_child = (self._focused_child - 1) % nr_childs

        focussed_child = self.get_child_objects()[self._focused_child]
        return EventPropagation.propagate_forward(focussed_child)

    def update(self, delta_time):
        w, h = self.size

        # position text boxes
        self._text_box_address.position = 1, 3
        self._text_box_address.size = w - 2, 3
        self._text_box_port.position = 1, 8
        self._text_box_port.size = w - 2, 3

        # highlight the focussed child
        for index, text_box_child in enumerate(self.get_child_objects()):
            text_box_child.use_cursor = index == self._focused_child

    def render(self, win):
        w, h = self.size
        win.erase()

        # border
        border_col_pair = get_colour_pair(1, 1, 1, 0, 0, 0)
        win.bkgd(border_col_pair)
        win.border()

        # draw the labels for the text boxes
        label_color = get_colour_pair(1, 1, 1, 0, 0, 0)
        render_text(
            win, "Server Address:", 1, 2, w - 2, 1, text_format=label_color)
        render_text(
            win, "Port:", 1, 7, w - 2, 1, text_format=label_color)
