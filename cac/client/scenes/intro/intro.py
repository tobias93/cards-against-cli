from cac.client.engine.game_object import Scene
from cac.client.engine.game_loop import Game
from cac.client.scenes.intro.title import TitleBox
from cac.client.scenes.select_server.select_server import SelectServerScene
from cac.client.engine.events_keyboard import KeyboardEvent
from cac.client.game_objects.background import HypnoBackground


class IntroScene(Scene):

    def __init__(self):
        super().__init__()
        self._title_shown = False
        self._titlebox = TitleBox()
        self._time = 0
        self._game: Game = None
        self._bg = HypnoBackground(transition_from=HypnoBackground())
        self._bg.transition_speed = 1.0 / 6

    def start_scene(self, game):
        self._game = game

    def stop_scene(self):
        pass

    def get_child_objects(self):
        return [self._bg, self._titlebox]

    def process_event(self, event):
        if isinstance(event, KeyboardEvent) and event.key_code == ord("\n"):
            self.next_scene()

    def update(self, delta_time):

        self._time += delta_time

        # show title
        if self._time > 1.7 and not self._title_shown:
            self._titlebox.open(20)
            self._title_shown = True

        # transition to the next scene
        if self._time > 6:
            self.next_scene()

        # position the title
        w, h = self.size
        border_size_x = int(max(min(w - 92, 20) / 2, 0))
        border_size_y = int(max(min(h - 18, 20) / 2, 0))
        self._titlebox.position = border_size_x, border_size_y
        self._titlebox.size = w - 2 * border_size_x, 0

        self._bg.position = 0, 0
        self._bg.size = self.size

    def next_scene(self):
        next_scene = SelectServerScene(self._bg)
        self._game.load_scene(next_scene)

    def render(self, win):
        pass
