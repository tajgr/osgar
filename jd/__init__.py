from threading import Thread, Lock
import urllib2

from lib import robot

def run():
    r = robot.Run()
    #canproxy = CANProxy(r)
    camera = Camera(r)
    #laser = Laser(r)
    #gps = GPS(r)

    yield robot

    robot.stop()

def replay(filepath):
    yield robot.Replay(filepath)

class Camera(Thread):
    def __init__(self, r):
        self.daemon = True
        self._queue = []
        self._lock = Lock()
        r.register_source(self.get)
        self.start()
    def get(self):
        with self._lock:
            ret = dict(camera=self._queue)
            self._queue = []
        return ret
    def run(self):
        while True:
            filepath = self.get_picure()
            with self._lock:
                self._queue.append(filepath)
    def get_picture(self):
        try:
            url = urllib2.urlopen(self.url)
            img = url.read()
            return self.robot.save_jpg(img)
        except IOError, e:
            print e
            return None
