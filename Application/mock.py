from time import sleep


class Scope:
    def __init__(self):
        pass

    def error_check(self):
        pass

    def save_setup(self):
        pass

    def recall_setup(self):
        pass

    def close(self, do_exit=True):
        pass


class ScopeManager(Scope):
    def __init__(self, channels=0, title=""):
        super().__init__()
        self.channels = channels
        self.title = title

    def set_channel(self, channels):
        self.channels = channels

    def set_title(self, title):
        self.title = title

    def initialize(self):
        pass

    def reinitialize(self):
        pass

    def acquire(self):
        sleep(2)
