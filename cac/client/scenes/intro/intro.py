from cac.client.engine.game_object import GameObject
from cac.client.helpers.audio import play_sound
from cac.client.helpers.colour import get_colour_pair_nr
from cac.client.helpers.text import render_text
from cac.client.scenes.intro.title import TitleBox


class IntroScene(GameObject):

    def __init__(self):
        super().__init__()
        self._audio_started = False
        self._title_shown = False
        self._titlebox = TitleBox()
        self._time = 0

    def get_child_objects(self):
        return [self._titlebox]

    def process_event(self, event_type, arg):
        pass

    def update(self, delta_time):

        self._time += delta_time

        # play the bg audio
        if not self._audio_started:
            play_sound("audio/intro.wav")
            self._audio_started = True
            self._time = 0

        # show title
        if self._time > 1.7 and not self._title_shown:
            self._titlebox.open(20)
            self._title_shown = True

        # position the title
        w, h = self.size
        self._titlebox.position = 10, 10
        self._titlebox.size = w - 20, 0

    def render(self, win):
        w, h = self.size
        render_text(
            win, "", 0, 0, w, h, fill_bg=" ",
            bg_colour_pair=get_colour_pair_nr(1, 1, 1, 0, 0, 0.2)
        )
