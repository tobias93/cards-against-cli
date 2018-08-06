
class Animation:

    def __init__(self, value):
        self.value = value
        self._running = False
        self._value_start = value
        self._value_end = value
        self._time = 0
        self._duration = 1

    def animate(self, duration, target_value):
        self._running = True
        self._value_start = self.value
        self._value_end = target_value
        self._time = 0
        self._duration = duration

    def stop(self):
        self._running = False

    def update(self, delta_time):
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
