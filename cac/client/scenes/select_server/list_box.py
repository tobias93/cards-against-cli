import curses

from cac.client.engine.game_object import GameObject
from cac.client.engine.curses_text import render_text
from cac.client.engine.curses_colour import get_colour_pair
from cac.client.engine.events_keyboard import KeyboardEvent


class ListBoxItem:
    """
    One entry of a listbox.
     - `caption` is the text to display for the item.
     - `info` is an array of lines(str), that provide additional
        information about the item.
        Those lines are rendered in grey below the caption.
     - `data` is an arbitrary object that can be used
       to store the data that is associated to this list box item.
    """

    def __init__(self, caption, info=[], data=None):
        self.caption = caption
        self.info = info
        self.data = data


class ListBox(GameObject):
    """
    List box ui component.
    Shows a list of items, from which one can be selected via Keyboard.

    How to use:

    >>> list_box = ListBox()
    ... list_box.items = [
    ...    ListBoxItem("Item one"),
    ...    ListBoxItem("Item two")
    ... ]

    Optionally, you can also customize colours using the following attributes:
     - fg_colour
     - bg_colour
     - info_fg_colour
     - info_bg_colour
     - selected_fg_colour
     - selected_bg_colour
     - selected_info_fg_colour
     - selected_info_bg_colour
     - border_fg_colour
     - border_bg_colour

    Items can be selected by pressing j or k. Or the arrow keys.
    Make sure to forward the corresponding keyboard events.
    It is your task to listen for the enter key or something to
    confirm the selection.

    The currently selected item can always be accessed using:
     > list_box.selected_item
    """

    def __init__(self):
        super().__init__()

        # list of ListBoxItem instances
        self.items = []

        # index of the selected list box item
        self._selected_item_index = 0

        # colours
        self.fg_colour = (0, 0, 0)
        self.bg_colour = (1, 1, 1)
        self.info_fg_colour = (.5, .5, .5)
        self.info_bg_colour = (1, 1, 1)
        self.selected_fg_colour = (0, 0, 0)
        self.selected_bg_colour = (.7, .7, .7)
        self.selected_info_fg_colour = (0, 0, 0)
        self.selected_info_bg_colour = (.7, .7, .7)
        self.border_fg_colour = (0, 0, 0)
        self.border_bg_colour = (1, 1, 1)

    def get_child_objects(self):
        return []

    def process_event(self, event):
        up_keys = [
            ord('k'),
            curses.KEY_UP,
        ]
        down_keys = [
            ord('j'),
            curses.KEY_DOWN,
        ]
        if isinstance(event, KeyboardEvent):
            if event.key_code in up_keys:
                self._selected_item_index -= 1
            elif event.key_code in down_keys:
                self._selected_item_index += 1

    def update(self, delta_time):

        # Make sure, that self._selected_item_index stays
        # within the valid bounds

        if self._selected_item_index >= len(self.items):
            self._selected_item_index = len(self.items) - 1

        if self._selected_item_index < 0:
            self._selected_item_index = 0

    @property
    def selected_item(self):
        if self._selected_item_index < len(self.items) \
                and self._selected_item_index >= 0:
            return self.items[self._selected_item_index]

    def render(self, win):
        w, h = self.size
        win.erase()

        # colours
        col_text = get_colour_pair(
            self.fg_colour,
            self.bg_colour)
        col_info = get_colour_pair(
            self.info_fg_colour,
            self.info_bg_colour)
        col_text_sel = get_colour_pair(
            self.selected_fg_colour,
            self.selected_bg_colour)
        col_info_sel = get_colour_pair(
            self.selected_info_fg_colour,
            self.selected_info_bg_colour)

        # background
        win.bkgd(col_text)

        # create a list of lines for the complete list box
        # and their respective colours
        lines = []
        selected_line = 0
        for index, item in enumerate(self.items):
            if index == self._selected_item_index:
                selected_line = len(lines)
                this_ite_col_text = col_text_sel
                this_ite_col_info = col_info_sel
            else:
                this_ite_col_text = col_text
                this_ite_col_info = col_info
            lines.append((this_ite_col_text, item.caption))
            lines.extend([(this_ite_col_info, info) for info in item.info])

        # choose, where to start rendering ("scrolling")
        # (if the list of lines is longer than the availible height)
        nr_lines = len(lines)
        first_line = selected_line - int(h / 2)
        if first_line + h - 1 >= nr_lines:
            first_line = nr_lines - h
        if first_line < 0:
            first_line = 0

        # draw the lines
        visible_lines = lines[first_line:first_line + h]
        for index, (colour, line) in enumerate(visible_lines):

            # draw the text in the chosen colour
            render_text(win, line, 0, index, w, 1,
                        text_format=colour, fill_bg=True)
