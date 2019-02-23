from cac.client.engine.game_object import GameObject
from cac.client.engine.curses_colour import get_colour_pair
from cac.client.engine.curses_text import render_text

class Label(GameObject):

    def __init__(self, text=""):
        super().__init__()
        self.text = text
        self.text_fg_colour=0, 0, 0
        self.text_bg_colour=1, 1, 1

    def get_child_objects(self):
        return []

    def update(self, delta_time):
        pass

    def process_event(self, event):
        pass

    def render(self, win):
        w, h = self.size

        # cls
        win.erase()

        # render text
        text_format = get_colour_pair(self.text_fg_colour, self.text_bg_colour)
        render_text(
            win, self.text,
            0, 0, w, h,
            text_format=text_format,
            fill_bg=True
        )
