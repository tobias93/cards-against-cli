import curses
from cac.client.engine.game_loop import Game
from cac.client.scenes.intro.intro import IntroScene


def main(curses_window):
    game = Game()
    scene = IntroScene()
    scene.size = 100, 100
    game.load_scene(scene)
    try:
        game.run(curses_window)
    except KeyboardInterrupt:
        return  # exit nicely, not with an exception


if __name__ == "__main__":
    curses.wrapper(main)
