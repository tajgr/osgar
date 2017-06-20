#!/usr/bin/python
"""
  Parallel processor/worker/filter for collected sensor data
"""
from multiprocessing import Process, Queue


def process_main(queue_in, queue_out):
    while True:
        data = queue_in.get()
        print "processing ...", data
        if data is None:
            break
        queue_out.put(data)


class Processor:
    def __init__(self, process_fn):
        self.queue_out = Queue()
        self.queue_in = Queue()
        self.processor = Process(target=process_main,
                                 args=(self.queue_out, self.queue_in))

    def get_result(self):
        if self.queue_in.empty():
            return None
        return self.queue_in.get()

    def start(self):
        self.processor.start()

    def push_back(self, data):
        print "Processor", data
        if self.queue_out.empty():
            self.queue_out.put_nowait(data)
        else:
            print "Skipped", data


# vim: expandtab sw=4 ts=4 

