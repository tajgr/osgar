"""
  Wrapper & timestamper of input/out over socket
"""

import socket
import urllib.request
from threading import Thread

from osgar.logger import LogWriter
from osgar.bus import BusShutdownException


class LogSocket:
    def __init__(self, socket, config, bus):
        self.socket = socket

        self.input_thread = Thread(target=self.run_input, daemon=True)
        self.output_thread = Thread(target=self.run_output, daemon=True)

        host = config.get('host')
        port = config.get('port')
        self.pair = (host, port)  # (None, None) for unknown address
        if 'timeout' in config:
            self.socket.settimeout(config['timeout'])
        self.bufsize = config.get('bufsize', 1024)

        self.bus = bus

    def _send(self, data):
        raise NotImplementedError()

    def start(self):
        self.input_thread.start()
        self.output_thread.start()

    def join(self, timeout=None):
        self.input_thread.join(timeout=timeout)
        self.output_thread.join(timeout=timeout)

    def run_input(self):
        while self.bus.is_alive():
            if self.pair == (None, None):  # unknown address
                self.bus.sleep(0.1)
                continue
            try:
                data = self.socket.recv(self.bufsize)
                if len(data) > 0:
                    self.bus.publish('raw', data)
            except socket.timeout:
                pass

    def run_output(self):
        try:
            while True:
                __, channel, data = self.bus.listen()
                if channel == 'raw':
                    self._send(data)
                elif channel == 'addr':
                    self.pair = tuple(data)
                    self.socket.connect(self.pair)
                else:
                    assert False, channel  # unsupported channel
 
        except BusShutdownException:
            pass

    def request_stop(self):
        self.bus.shutdown()


class LogTCPStaticIP(LogSocket):
    """
      TCP driver for existing static IP (i.e. SICK LIDAR)
    """
    def __init__(self, config, bus):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        LogSocket.__init__(self, soc, config, bus)

        self.socket.connect(self.pair)

    def _send(self, data):
        self.socket.send(data)


class LogTCPDynamicIP(LogSocket):
    """
      TCP driver for dynamic previously unknown address
         (ROS proxy for subscribers)
    """

    def __init__(self, config, bus):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        LogSocket.__init__(self, soc, config, bus)

    def _send(self, data):
        self.socket.send(data)


class LogTCPServer(LogSocket):
    """
      TCP driver for server side - prepare connection and wait
      for others to connect (ROS proxy for publishers)
    """

    def __init__(self, config, bus):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        LogSocket.__init__(self, soc, config, bus)

        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.bind(self.pair)

    def _send(self, data):
        self.socket.send(data)

    def run_input(self):
        print("Waiting ...")
        self.socket.listen(1)
        print("end of listen")
        self.socket, addr = self.socket.accept()
        print('Connected by', addr)
        super().run_input()

class LogUDP(LogSocket):
    def __init__(self, config, bus):
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        LogSocket.__init__(self, soc, config, bus)
        self.socket.bind(('', self.pair[1]))

    def _send(self, data):
        self.socket.sendto(data, self.pair)


class LogHTTP:
    def __init__(self, config, bus):
        self.input_thread = Thread(target=self.run_input, daemon=True)

        self.url = config['url']
        self.bus = bus

    def start(self):
        self.input_thread.start()

    def join(self, timeout=None):
        self.input_thread.join(timeout=timeout)

    def run_input(self):
        while self.bus.is_alive():
            try:
                with urllib.request.urlopen(self.url) as f:
                    data = f.read()
                if len(data) > 0:
                    self.bus.publish('raw', data)
            except socket.timeout:
                pass

    def request_stop(self):
        self.bus.shutdown()


if __name__ == "__main__":
    import time
    from osgar.bus import BusHandler

    config = {'host':'localhost', 'port': 8001, 'timeout': 1.0}
    log = LogWriter(prefix='test-tcp-')
    device = LogTCP(config, bus=BusHandler(log, out={'raw':[]}))
    device.start()
    time.sleep(2)
    device.request_stop()
    device.join()

# vim: expandtab sw=4 ts=4
