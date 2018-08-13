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

    def __init__(self):
        super().__init__()

        # list of ListBoxItem instances
        self.items = []

        # index of the selected list box item
        self._selected_item_index = 0

        # colours
        self.fg_colour = (1, 1, 1)
        self.bg_colour = (0, 0, 0)
        self.info_fg_colour = (.5, .5, .5)
        self.info_bg_colour = (0, 0, 0)
        self.selected_fg_colour = (0, 0, 0)
        self.selected_bg_colour = (1, 1, 1)
        self.selected_info_fg_colour = (.0, .0, .0)
        self.selected_info_bg_colour = (1, 1, 1)
        self.border_fg_colour = (1, 1, 1)
        self.border_bg_colour = (0, 0, 0)

    def get_child_objects(self):
        return []

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.is_ascii_key('j'):
                self._selected_item_index += 1
            elif event.is_ascii_key('k'):
                self._selected_item_index -= 1

    def update(self, delta_time):

        # Make sure, that self._selected_item_index stays
        # within the valid bounds

        if self._selected_item_index >= len(self.items):
            self._selected_item_index = len(self.items) - 1

        if self._selected_item_index < 0:
            self._selected_item_index = 0

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
        col_info = get_colour_pair(
            self.info_fg_colour,
            self.info_bg_colour)
        col_text_sel = get_colour_pair(
            self.selected_fg_colour,
            self.selected_bg_colour)
        col_info_sel = get_colour_pair(
            self.selected_info_fg_colour,
            self.selected_info_bg_colour)

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

        # available space without border
        items_w = w - 2
        items_h = h - 2

        # choose, where to start rendering ("scrolling")
        # (if the list of lines is longer than the availible height)
        nr_lines = len(lines)
        first_line = selected_line - int(items_h / 2)
        if first_line + items_h - 1 >= nr_lines:
            first_line = nr_lines - items_h
        if first_line < 0:
            first_line = 0

        # draw the lines
        visible_lines = lines[first_line:first_line + items_h]
        for index, (colour, line) in enumerate(visible_lines):

            # draw the text in the chosen colour
            render_text(win, line, 1, index + 1, items_w, 1,
                        text_format=colour, fill_bg=True)
