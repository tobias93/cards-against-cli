
class Animation:
    """
    "Animates" a value by slowly changing it from
    it's current value to it's target value over time.
    """

    def __init__(self, value):
        """
        :param value: The initial value of the animated value
        """
        self.value = value
        self._running = False
        self._value_start = value
        self._value_end = value
        self._time = 0
        self._duration = 1

    def animate(self, duration, target_value):
        """
        Starts an animation.
        The current value will be transitioned to the
        given target value in the given time (parameter duration)
        """
        self._running = True
        self._value_start = self.value
        self._value_end = target_value
        self._time = 0
        self._duration = duration

    def stop(self):
        """
        Stops the currently running animation.
        """
        self._running = False

    def update(self, delta_time):
        """
        Updates the current value.
        This method should be called every iteration of the game loop.
        :param delta_time: The time passed since the last call to update()
        """
        if not self._running:
            return
        self._time += delta_time

        if self._time >= self._duration:
            self._running = False
            self.value = self._value_end
        else:
            self.value = self._value_start  \
                + (self._value_end - self._value_start) \
                * self._time / self._duration
