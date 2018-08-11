from cac.client.engine.game_object import GameObject
from cac.client.engine.curses_text import render_text
from cac.client.engine.curses_colour import get_colour_pair_nr
from cac.client.engine.events_keyboard import KeyboardEvent


class ListBoxItem:
    """
    One entry of a listbox.
     - `caption` is the text to display for the item.
     - `data` is an arbitrary object that can be used
       to store the data that is associated to this list box item.
    """

    def __init__(self, caption, data):
        self.caption = caption
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
        self.selected_fg_colour = (0, 0, 0)
        self.selected_bg_colour = (1, 1, 1)

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

        # choose, where to start ("scrolling")
        # (if the list of items is longer than the availible height)
        nr_items = len(self.items)
        first_item = self._selected_item_index - int(h / 2)
        if first_item + h - 1 >= nr_items:
            first_item = nr_items - h
        if first_item < 0:
            first_item = 0

        # draw the items
        visible_items = self.items[first_item:first_item + h]
        for index, item in enumerate(visible_items, first_item):

            # choose a colour based on if the item is selected.
            selected = index == self._selected_item_index
            if selected:
                colour = get_colour_pair_nr(*(
                    self.selected_fg_colour + self.selected_bg_colour))
            else:
                colour = get_colour_pair_nr(*(self.fg_colour + self.bg_colour))

            # draw the text in the chosen colour
            render_text(win, item.caption, 0, index, w, 1,
                        text_colour_pair=colour, fill_bg=True)
