from pathlib import Path
import math
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
    def __init__(self, channels=None, title=""):
        super().__init__()
        self.channels = channels if channels is not None else [True, True, True, True]
        self.title = title
        self.current_iteration = 0

    def set_channel(self, channels):
        self.channels = channels

    def set_title(self, title):
        self.title = title

    def initialize(self):
        self.current_iteration = 0
        directory = Path.cwd().parent / 'results'
        (directory / self.title).mkdir(parents=True, exist_ok=True)

    def reinitialize(self):
        pass

    def acquire(self):
        sleep(0.5)  # Simulate hardware acquisition time
        self.current_iteration += 1
        
        directory = Path.cwd().parent / 'results'
        filename = directory / self.title / f"{self.title}_{self.current_iteration}.csv"
        
        # Write 200 data points of simulated wave forms:
        # Format: time, ch1, ch2, ch3, ch4
        with filename.open("w") as f:
            for idx in range(200):
                t = -0.01 + (idx * 0.0001)
                
                # Check which channels are enabled (converting truthy values)
                ch1_val = math.sin(2 * math.pi * 50 * t) if self.channels[0] else 0.0
                ch2_val = math.cos(2 * math.pi * 50 * t) if self.channels[1] else 0.0
                ch3_val = (1.0 if (idx // 20) % 2 == 0 else -1.0) if self.channels[2] else 0.0
                ch4_val = (t * 100.0) if self.channels[3] else 0.0
                
                f.write(f"{t:.6e},{ch1_val:.6e},{ch2_val:.6e},{ch3_val:.6e},{ch4_val:.6e}\n")

