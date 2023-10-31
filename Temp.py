import time
import threading

class Temp:
    def __init__(self, seconds):
        self.init_seconds = seconds
        self.seconds = seconds
        self._thread = None
        self._stop_event = threading.Event()

    def _run(self):
        while self.seconds and not self._stop_event.is_set():
            mins, secs = divmod(self.seconds, 60)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            print(timeformat, end='\r')
            time.sleep(1)
            self.seconds -= 1
        else:
            self._thread = None

        if not self._stop_event.is_set():
            if self.callback:
                self.callback()

    def start(self, callback=None):
        self.callback = callback
        self.seconds = self.init_seconds
        if self._thread is None:
            self._thread = threading.Thread(target=self._run)
            self._thread.start()

    def stop(self, callback=None):
        if self._thread:
            self._stop_event.set()
            self._thread.join()  
            self._thread = None
            if callback:
                callback()
    def is_running(self):
        return self._thread is not None
