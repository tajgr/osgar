
import ast
from datetime import datetime, timedelta
import time

_fmt = "%Y-%m-%dT%H:%M:%S.%f"

class Run:
    def __init__(self, step=timedelta(milliseconds=50)):
        self._start = datetime.now()
        self._step = step
        self._sources = []
        self._extensions = []
        self._sinks = []
        filepath = "something.log"
        self._log = open(filepath, "w")
        self._log.write(str(self._start.strftime(_fmt)) + "\n")
        self._next_wakeup = self._start + self._step

    def __del__(self):
        self._log.close()

    def register_source(self, source):
        self._sources.append(source)

    def register_extension(self, ext):
        self._extensions.append(ext)

    def update(self, commands):
        self._now = datetime.now() - self._start
        if self._next_wakeup > self._now:
            time.sleep((self._next_wakeup - self._now).total_seconds())
            self._now = datetime.now() - self._start
        else:
            assert self._now - self._next_wakeup < self._step/10, "late by more than 0.1 step"
        self._next_wakeup += self._step
        self._log.write(str(self._now.__reduce__()[1]) + "\n")
        self._log.write(str(commands) + "\n")
        for sink in self._sinks:
            sink(commands)
        data = {}
        for source in self._sources:
            data.update(source())
        self._log.write(str(data) + "\n")
        for ext in self._extensions:
            ext(data)
        return data

    @property
    def now(self):
        "relative timedelta since start"
        return self._now

    def save_jpg(self, img):
        # todo save somewhere and return 'key'
        return "nothing for now"

    def load_jpg(self, key):
        # todo
        return None


class Replay():
    def __init__(self, filepath):
        self._log = open(filepath, "r")
        self._extensions = []
        self._start = datetime.strptime(self._log.readline().strip(), _fmt)

    def register_extension(self, ext):
        self._extensions.append(ext)

    def update(self, commands):
        "reads timestamp, commands and data from log"
        self._now = timedelta(*ast.literal_eval(self._log.readline().strip()))
        logged_commands = ast.literal_eval(self._log.readline().strip())
        assert commands == logged_commands
        data = ast.literal_eval(self._log.readline().strip())
        for ext in self._extensions:
            ext(data)
        return data

    @property
    def now(self):
        "relative timedelta since start"
        return self._now
