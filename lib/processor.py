#!/usr/bin/python
"""
  Parallel processor/worker/filter for collected sensor data
"""
from multiprocessing import Pool


g_pool = None


class Processor:
    def __init__(self, process_fn):
        global g_pool
        g_pool = Pool(processes=1)
        self.process_fn = process_fn
        self.processing = None

    def get_result(self):
        global g_pool
        if self.processing is None or self.processing.ready():
            return None
        ret = self.processing.get()
        self.processing = None
        return ret

    def start(self):
        pass  # only legacy function

    def requestStop(self):
        global g_pool
        g_pool.close()


    def push_back(self, data):
        global g_pool
        print "Processor", data
        if not self.processing:
            self.processing = g_pool.apply_async(self.process_fn, (data,))
        else:
            print "Skipped", data

# vim: expandtab sw=4 ts=4 

