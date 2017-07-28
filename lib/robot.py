
import ast

class Run:
    def __init__(self):
        self._sources = []
        self._extensions = []
        self._sinks = []
        filepath = "something.log"
        self._log = open(filepath, "w")

    def __del__(self):
        self._log.close()

    def register_source(self, source):
        self._sources.append(source)

    def register_extension(self, ext):
        self._extensions.append(ext)

    def update(self, commands):
        for sink in self._sinks:
            sink(commands)
        # todo log commands
        data = {}
        for source in self._sources:
            data.update(source())
        self._log.write(str(data)+"\n")
        for ext in self._extensions:
            ext(data)
        return data

    def save_jpg(self, img):
        # todo save somewhere and return 'key'
        return "nothing for now"

    def load_jpg(self, key):
        # todo
        return None


class Replay():
    def __init__(self, filepath):
        self._log = open(filepath, "r")
        self._extenstions = []

    def register_extension(self, ext):
        self._extensions.append(ext)

    def update(self, commands):
        # todo handle commands
        data = ast.literal_eval(self._log.readline())
        for ext in self._extensions:
            ext(data)
        return data
