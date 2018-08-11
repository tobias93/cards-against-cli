import curses

from cac.client.engine.events import EventSource, Event


class KeyboardEvent(Event):

    def __init__(self, key_code):
        super().__init__()
        self.key_code = key_code

    def is_ascii_key(self, key):
        return self.key_code == ord(key)


class KeyboardEventSource(EventSource):

    def __init__(self):
        self._win = curses.newwin(1, 1)
        self._win.nodelay(1)

    def get_events(self):
        key = self._win.getch()
        if key != -1:
            return [KeyboardEvent(key)]
        else:
            return []
