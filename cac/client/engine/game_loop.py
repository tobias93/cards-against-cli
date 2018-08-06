import curses
import time
from enum import Enum


class EventType(Enum):
    KEY_DOWN = 1
    KEY_UP = 2


class Game:

    def __init__(self):
        self._current_scene = None
        self._max_framerate = 25

    def exit(self):
        self.load_scene(None)

    def load_scene(self, main_game_object):
        self._current_scene = main_game_object

    def run(self, curses_window=None):
        """
        Initializes the game end then runs the game loop.
        Terminates once the game has exited (call to self.exit()).
        """

        # curses
        if curses_window is None:
            return curses.wrapper(self.run)
        curses.curs_set(0)
        curses_window.nodelay(True)

        # keyboard
        last_key = ""

        # init
        last_frame_time = time.time()
        min_frame_time = 1.0 / self._max_framerate
        render_exception_cnt = 0

        # the game loop
        while self._current_scene is not None:

            # work with the current scene
            scene = self._current_scene
            if scene is None:
                continue

            # time
            this_frame_time = time.time()
            wait_time = last_frame_time + min_frame_time - this_frame_time
            if wait_time > 0:
                time.sleep(wait_time)
                this_frame_time = time.time()
            delta_time = this_frame_time - last_frame_time
            last_frame_time = this_frame_time

            # process events
            # keyboard
            try:
                key = curses_window.getkey()
            except Exception:
                key = ""    # no key was pressed

            if last_key != "" and key != last_key:
                scene.process_event(EventType.KEY_UP, last_key)
            if key != "" and key != last_key:
                scene.process_event(EventType.KEY_DOWN, key)

            last_key = key

            # update game state
            self._recursive_update(scene, delta_time)

            # Force the scene to fill the entire terminal
            scene.position = 0, 0
            scene_w, scene_h = scene.size
            if curses.is_term_resized(scene_h, scene_w):
                h, w = curses_window.getmaxyx()
                curses.resizeterm(h, w)
                scene.size = w, h
                render_exception_cnt = 0

            # draw
            try:
                self._recursive_draw(scene, 0, 0, False)
                curses.doupdate()
                render_exception_cnt = 0
            except Exception:
                # count the number of exceptions - it is ok,
                # if exceptions get raised - this might for
                # example happen, when the window is resized.
                # just to many successive exceptions are not that good...
                render_exception_cnt += 1
                if render_exception_cnt > 3:
                    raise

    def _recursive_update(self, game_object, delta_time):
        """
        Calls the update method on the given game_object
        as well as on all children (recursively).
        """

        # update the game object itself
        game_object.update(delta_time)

        # update all child game objects
        children = game_object.get_child_objects()
        for child_object in children:
            self._recursive_update(child_object, delta_time)

    def _recursive_draw(self, game_object, base_x, base_y, base_mooved):

        # quick access to the game object and the housekeeping object
        go = game_object
        hk = game_object.housekeeping

        # make sure, a render pad of the correct size exists
        w, h = go.size
        x, y = go.position
        visible = w > 0 and h > 0
        if base_mooved:
            hk.mooved = True
        if hk.render_pad is None and visible:
            hk.render_pad = curses.newpad(h, w)
        else:
            if hk.resized and visible:
                hk.render_pad.resize(h, w)

        # rerender it
        if w != 0 and h != 0 and visible:
            go.render(hk.render_pad)
            # todo clip coordinates, so that curses does not
            # throw an exception when the window is too small
            hk.render_pad.noutrefresh(0, 0, y, x, y + h - 1, x + w - 1)

        # recursively render subwindows
        children = go.get_child_objects()
        for child_object in children:
            self._recursive_draw(
                child_object,
                base_x + x, base_y + y,
                hk.mooved or base_mooved)

        # reset flags, prepare for next draw
        hk.resized = False
        hk.mooved = False
