from cac.client.engine.game_object import GameObject
from cac.client.engine.curses_colour import get_colour_pair

class UiFrame(GameObject):

    def __init__(self):
        super().__init__()

    def get_child_objects(self):
        return []

    def update(self, delta_time):
        pass

    def process_event(self, event):
        pass

    def render(self, win):
        
        # make a  white bg
        win.erase()
        win.bkgd(get_colour_pair(0, 0, 0, 1, 1, 1))

        # black border
        win.border()
