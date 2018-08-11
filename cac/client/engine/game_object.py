from abc import ABC, abstractmethod


class GameObjectHouseKeeping:
    """
    Stores information about a game object, that is needed
    by the game loop to do it's "house keeping work".
    """

    def __init__(self):
        self.render_pad = None
        self.resized = False
        self.mooved = False


class GameObject(ABC):
    """
    Represents one "thing" in a game.
    """

    def __init__(self):
        self._pos_x = 0
        self._pos_y = 0
        self._width = 1
        self._height = 1
        self.housekeeping = GameObjectHouseKeeping()

    @property
    def size(self):
        """
        The size of the game object in characters
        as a tuple of the form (width, height)
        """
        return self._width, self._height

    @size.setter
    def size(self, value):
        w, h = value
        if w != self._width or h != self._height:
            self.housekeeping.resized = True
            self._width = w
            self._height = h

    @property
    def position(self):
        """
        The position of the game object relative
        to the position of its parent object.
        The position is given in characters as a
        tuple of the form (x, y)
        """
        return self._pos_x, self._pos_y

    @position.setter
    def position(self, value):
        x, y = value
        if x != self._pos_x or y != self._pos_y:
            self.housekeeping.mooved = True
            self._pos_x = x
            self._pos_y = y

    @abstractmethod
    def get_child_objects(self):
        """
        Should return a list of all child game objects.
        """
        raise NotImplementedError()

    @abstractmethod
    def process_event(self, type, arg):
        """
        Is called, when an event occurs.

        Note: Unlike update() and render(), this is not called recursively
        automatically. Every game object must manually forward events
        to its children, if it whiches them to receive the events.
        The idea of this is to let game objects maintain something
        like a "focus" and let them only forward events to the
        currently "focussed" child.
        """
        raise NotImplementedError()

    @abstractmethod
    def update(self, delta_time):
        """
        Will be called once every game loop iteration.
        The state of the game object should be adapted here.
        The parameter delta_time gives the time since the
        last call to update in seconds as a float. This can
        be used to implement smooth animations.
        """
        raise NotImplementedError()

    @abstractmethod
    def render(self, pad):
        """
        Should draw the game object onto the given curses pad.
        """
        raise NotImplementedError()


class Scene(GameObject):
    """
    A scene is a "special" game object.
    It is the root of the tree of game objects ("Scene graph").
    There is always exactly one active scene in a game.
    A scene can be loaded into the game and made active by
    calling the load_scene() method of the
    cac.client.engine.game_loop.Game class with a Scene instance.
    """

    @abstractmethod
    def start_scene(self, game):
        """
        Will be called after the scene was loaded
        using the load_scene() method of the game.
        """
        raise NotImplementedError()

    @abstractmethod
    def stop_scene(self):
        """
        This method will be called when the scene
        becomes inactive. This happens in the following cases:
            - An other scene is loaded using the load_scene()
              method of the game
            - The game is over. The application will exit.
            - The application exits, because the user pressed Ctrl-C.
        """
        raise NotImplementedError()
