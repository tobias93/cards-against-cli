import curses
from cac.client.engine.game_object import GameObject
from cac.client.engine.curses_sprite import Sprite
from cac.client.engine.curses_colour import get_colour_pair_nr
from cac.client.engine.animation import Animation


class TitleBox(GameObject):

    def __init__(self):
        super().__init__()

        # welcome sprite
        self._title = Sprite("sprites/title.txt")

        # opening animation
        self._opening_animation = Animation(0)

    def open(self, height):
        self._opening_animation.animate(2, height)

    def get_child_objects(self):
        return []

    def process_event(self, event_type, arg):
        pass

    def update(self, delta_time):
        self._opening_animation.update(delta_time)
        w, h = self.size
        self.size = w, int(self._opening_animation.value)

    def render(self, win):

        # make a  white bg
        win.erase()
        win.bkgd(curses.color_pair(get_colour_pair_nr(0, 0, 0, 1, 1, 1)))

        # show the title sprite, centered
        w, h = self.size
        sprite_w, sprite_h = self._title.size
        x = int(w / 2 - sprite_w / 2)
        y = int(h / 2 - sprite_h / 2)
        self._title.draw(win, x, y)

        win.border()
