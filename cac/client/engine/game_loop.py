import curses
import time

from cac.client.engine.game_object import Scene
from cac.client.engine.events import EventPropagation


class Game:

    def __init__(self):
        self._current_scene = None
        self._max_framerate = 25
        self._event_sources = []

    def exit(self):
        self._current_scene = None

    def load_scene(self, main_game_object):
        assert isinstance(main_game_object, Scene)
        self._current_scene = main_game_object

    def add_event_source(self, event_source):
        self._event_sources.append(event_source)

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

        # init
        last_frame_time = time.time()
        min_frame_time = 1.0 / self._max_framerate
        render_exception_cnt = 0
        scene = None

        # the game loop
        while self._current_scene is not None:

            # work with the current scene
            if scene is not self._current_scene:

                # stop the old scene
                if scene is not None:
                    scene.stop_scene()

                # start the new scene
                scene = self._current_scene
                if scene is not None:
                    scene.start_scene(self)
                else:
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
            for evt_src in self._event_sources:
                events = evt_src.get_events()
                for event in events:
                    self._recursive_process_event(scene, event)

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
                self._recursive_draw(scene, 0, 0, scene_w, scene_h, False)
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

        # game loop terminated.
        # stop the last scene.
        if scene is not None:
            scene.stop_scene()

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

    def _recursive_draw(self, game_object,
                        base_x, base_y, base_w, base_h,
                        base_mooved):

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

            # render it into the dedicated pad
            go.render(hk.render_pad)

            # draw the pad on the screen.
            # clip coordinates, on the parent go
            pad_min_x = 0
            pad_min_y = 0
            screen_min_x = base_x + x
            screen_min_y = base_y + y
            screen_max_x = base_x + x + w - 1
            screen_max_y = base_y + y + h - 1
            base_max_x = base_x + base_w - 1
            base_max_y = base_y + base_h - 1
            if screen_min_x < base_x:
                pad_min_x += base_x - screen_min_x
                screen_min_x = base_x
            if screen_min_y < base_y:
                pad_min_y += base_y - screen_min_y
                screen_min_y = base_y
            if screen_max_x > base_max_x:
                screen_max_x = base_max_x
            if screen_max_y > base_max_y:
                screen_max_y = base_max_y
            if screen_max_x >= screen_min_x and screen_max_y >= screen_min_y:
                hk.render_pad.noutrefresh(
                    pad_min_y, pad_min_x,
                    screen_min_y, screen_min_x, screen_max_y, screen_max_x
                )

        # recursively render subwindows
        children = go.get_child_objects()
        for child_object in children:
            self._recursive_draw(
                child_object,
                base_x + x, base_y + y, w, h,
                hk.mooved or base_mooved)

        # reset flags, prepare for next draw
        hk.resized = False
        hk.mooved = False

    def _recursive_process_event(self, game_object, event):
        """
        Calls the process_event method on the given game_object
        as well as on all children (depending on how the GameObject)
        chooses to propagate the event.
        """

        # process the event
        propagation = game_object.process_event(event)

        # do not propagate by default
        if propagation is None:
            propagation = EventPropagation.propagate_none()

        # propagate the event to the children

        # no propagation
        if propagation.should_not_propagate():
            return

        # recursively propagate to all children
        elif propagation.should_propagate_all():
            children = game_object.get_child_objects()
            for child_object in children:
                self._recursive_process_event(child_object, event)

        # propagate just to a single child object
        # (good for ui focus management)
        elif propagation.should_forward():
            child_object = propagation.get_forwarded_game_object()
            if child_object is not None:
                self._recursive_process_event(child_object, event)

        else:
            raise RuntimeError("Bad propagation info")
