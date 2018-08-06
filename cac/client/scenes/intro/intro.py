from cac.client.engine.game_object import GameObject
from cac.client.helpers.text import render_text
from cac.client.helpers.text import TextAlignment, VerticalTextAlignment
from cac.client.helpers.colour import get_colour_pair_nr
from cac.client.helpers.sprite import Sprite
from cac.client.helpers.audio import play_sound


class IntroScene(GameObject):

    def __init__(self):
        super().__init__()
        self._audio_started = False
        self._time = 0
        self._title = Sprite("sprites/title.txt")

    def get_child_objects(self):
        return []

    def process_event(self, event_type, arg):
        pass

    def update(self, delta_time):

        # keep track of the time of the audio file.
        self._time += delta_time

        # play the bg audio
        if not self._audio_started:
            play_sound("audio/intro.wav")
            self._audio_started = True
            self._time = 0

    def render(self, win):
        w, h = self.size

        # reset
        win.erase()
        render_text(
            win, f"Hello World!",
            1, 1, w - 2, h - 2,
            word_wrap=True,
            fill_bg=" ",
            alignment=TextAlignment.CENTER,
            valignment=VerticalTextAlignment.CENTER,
            text_colour_pair=get_colour_pair_nr(1, 0, 0, 0, 1, 1),
            bg_colour_pair=get_colour_pair_nr(0.5, 0.25, 0, 0.5, 0.5, 0)
        )
        #win.border()
        self._title.draw(win, 5, 5)
