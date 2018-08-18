import curses

from cac.client.engine.game_object import GameObject
from cac.client.engine.curses_text import render_text
from cac.client.engine.curses_colour import get_colour_pair
from cac.client.engine.events_keyboard import KeyboardEvent


class TextBox(GameObject):
    """
    Text box ui component.
    A text field where the user can enter Text.
    """

    def __init__(self):
        super().__init__()

        # The text that the user entered
        self.text = ""

        # The index of the character where the cursor is.
        self.cursor_pos = 0
        self.use_cursor = False

        # colours
        self.fg_colour = (1, 1, 1)
        self.bg_colour = (0, 0, 1)
        self.border_fg_colour = (1, 1, 1)
        self.border_bg_colour = (0, 1, 0)

    def get_child_objects(self):
        return []

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):

            # make sure the cursor position is valid:
            if self.cursor_pos < 0:
                self.cursor_pos = 0
            if self.cursor_pos > len(self.text):
                self.cursor_pos = len(self.text)

            # printable characters
            if event.key_code >= ord(' ') and event.key_code <= ord('~'):
                self.text = self.text[:self.cursor_pos] + \
                    chr(event.key_code) + \
                    self.text[self.cursor_pos:]
                self.cursor_pos += 1

            # arrow keys
            if event.key_code == curses.KEY_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            if event.key_code == curses.KEY_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)

            # backspace
            if event.key_code in [curses.KEY_BACKSPACE, 127]:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + \
                        self.text[self.cursor_pos:]
                    self.cursor_pos -= 1

            # del
            if event.key_code == curses.KEY_DC:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + \
                        self.text[self.cursor_pos + 1:]

    def update(self, delta_time):
        pass

    def render(self, win):
        w, h = self.size
        win.erase()

        # border
        border_col_pair = get_colour_pair(
            self.border_fg_colour, self.border_bg_colour)
        win.bkgd(border_col_pair)
        win.border()

        # colours
        col_text = get_colour_pair(
            self.fg_colour,
            self.bg_colour)
        col_cursor = get_colour_pair(0, 0, 0, 1, 0, 0)

        # calculate the positions
        text_w = w - 2
        if self.cursor_pos < text_w:
            start_char = 0
            cursor_position = self.cursor_pos + 1
        else:
            start_char = self.cursor_pos - text_w + 1
            cursor_position = text_w

        # draw the text
        render_text(
            win, self.text[start_char:], 1, 1, text_w, 1,
            text_format=col_text
        )

        # draw the cursor
        char_under_cursor = (self.text + ' ')[self.cursor_pos]
        if self.use_cursor:
            render_text(
                win, char_under_cursor, cursor_position, 1, 1, 1,
                text_format=col_cursor
            )
