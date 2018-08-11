from abc import ABC, abstractmethod


class Event(ABC):
    """
    Base class for all events.
    """

    def __init__(self):
        pass


class EventSource(ABC):
    """
    Base class for a event sources.
    Event sources produce events of a specific type.
    They can be added to the game  so that events produced by
    this event source will be processed during the game loop.
    """

    @abstractmethod
    def get_events(self):
        """
        Will be called during each game loop iteration and
        is supposed to return a list of events, that have been
        occured since the last call to get_events.
        """
        raise NotImplementedError()


class EventPropagation:
    """
    Describes, how an event should be propagated.

    Every GameObject, that handles an event in the process_event() method,
    should return a value that indicates, how the event should be further
    processed. The return value of process_event() controls, to which
    child GameObjects the event should be propagated.
    """

    def __init__(self, propagation_type, child=None):
        self._propagation_type = propagation_type
        self._child = child

    def should_not_propagate(self):
        return self._propagation_type == 0

    def should_propagate_all(self):
        return self._propagation_type == 1

    def should_forward(self):
        return self._propagation_type == 2

    def get_forwarded_game_object(self):
        return self._child

    @staticmethod
    def propagate_none():
        """
        Creates an event propagation,
        that tells the game loop to stop processing this event.
        """
        return EventPropagation(0, None)

    @staticmethod
    def propagate_all():
        """
        Creates an event propagation,
        that tells the game loop to recursively
        process this event in all child game object.
        """
        return EventPropagation(1, None)

    @staticmethod
    def propagate_forward(child):
        """
        Creates an event propagation,
        that tells the game loop to recursively
        process this event just in the one
        given child game object.
        """
        return EventPropagation(2, child)
