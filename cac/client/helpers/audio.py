from cac.client.helpers.assets import get_asset_file
import wave
from simpleaudio import WaveObject


def play_sound(asset_name):
    if not audio_enabled:
        return

    file = get_asset_file(asset_name)
    wav = wave.open(file, 'rb')
    audio = WaveObject.from_wave_read(wav)
    audio.play()


# test, if audio works in the current environment.
# we need to do that here, before curses has a chance to be initialized.
# so that no outpiut (error messages...) can interfer with the curses output.
audio_enabled = True
try:
    play_sound("audio/silence.wav")
except Exception:
    audio_enabled = False
