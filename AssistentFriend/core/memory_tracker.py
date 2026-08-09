import time

class MemoryTracker:
    def __init__(self):
        self.start_time = time.time()
        self.ignored_duration = 0
        
    def mark_interaction(self):
        self.ignored_duration = 0
        
    def tick(self):
        self.ignored_duration += 1
        return self.ignored_duration