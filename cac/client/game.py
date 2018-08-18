import os.path
import curses
from cac.client.engine.game_loop import Game
from cac.client.engine.events_keyboard import KeyboardEventSource
from cac.client.engine.asset_loader import load_assets_from_folder
from cac.client.scenes.intro.intro import IntroScene
from cac.client.scenes.select_server.select_server import \
    ReplaceWithServerException
from cac.server.server import main as server_main


def main(curses_window):

    # load assets
    asset_path = os.path.join(os.path.dirname(__file__), "assets")
    load_assets_from_folder(asset_path)

    # load game with the into scene
    game = Game()
    game.add_event_source(KeyboardEventSource())
    scene = IntroScene()
    game.load_scene(scene)

    # run until the game exits or ctrl-c is pressed
    try:
        game.run(curses_window)
    except KeyboardInterrupt:
        return  # exit nicely, not with an exception


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except ReplaceWithServerException:
        server_main()
