import time


class AFKDetector:
    def __init__(self, timeout=4):
        self.timeout = timeout
        self.last_action_time = time.time()

    def update_last_action_time(self, *args):
        self.last_action_time = time.time()

    def is_afk(self):
        return time.time() - self.last_action_time > self.timeout
