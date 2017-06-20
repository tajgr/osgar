#!/usr/bin/python
"""
  Parallel processor/worker/filter for collected sensor data
"""
from multiprocessing import Process, Queue


g_index = 0
g_queue_out = None
g_processor = None
g_queue_in = None


def process_main(queue_in, queue_out, process_fn):
    global g_index
    while True:
        data = queue_in.get()
        print "processing ...", data
        if data is None:
            break
        ret = process_fn(data)  # TODO replace by parameter
        queue_out.put_nowait((g_index, ret))
        g_index += 1
        print "waiting ..."


class Processor:
    def __init__(self, process_fn):
        # process_fn is now ignored - how to pass it to second interpreter??
        global g_queue_out, g_processor, g_queue_in
        g_queue_out = Queue()
        g_queue_in = Queue()
        self.processing = False
        g_processor = Process(target=process_main,
                              args=(g_queue_out, g_queue_in, process_fn))

    def get_result(self):
        global g_queue_in
        if g_queue_in.empty():
            return None
        ret = g_queue_in.get()
        self.processing = False
        return ret

    def start(self):
        global g_processor
        g_processor.start()

    def requestStop(self):
        global g_queue_out
        g_queue_out.put_nowait(None)

    def push_back(self, data):
        global g_queue_out
        print "Processor", data
        if not self.processing:
            self.processing = True
            g_queue_out.put_nowait(data)
        else:
            print "Skipped", data

# vim: expandtab sw=4 ts=4 

