import time
import threading

class Temp:
    def __init__(self, seconds, alignment=10, text=""):
        self.init_seconds = seconds
        self.seconds = seconds
        self._thread = None
        self._stop_event = threading.Event()
        self.__alignment = alignment 
        self.__text = text
        self.callback = None

    def _run(self):
        while self.seconds and not self._stop_event.is_set():
            mins, secs = divmod(self.seconds, 60)
            timeformat = '{: >{align}}'.format('{text}{:02d}:{:02d}'.format(mins, secs, text=self.__text), align=self.__alignment, text=self.__text)
            print(timeformat, end='\r')
            time.sleep(1)
            self.seconds -= 1

        if self._stop_event.is_set():
            self._stop_event.clear()
        else:
            if self.callback:
                self.callback()

        self._thread = None

    def start(self, callback=None):
        self.callback = callback
        self.seconds = self.init_seconds
        if self._thread is None:
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run)
            self._thread.start()

    def stop(self, callback=None):
        if self._thread:
            self._stop_event.set()
            self._thread.join()
            self._thread = None
            self._stop_event.clear()
            if callback:
                callback()

    def is_running(self):
        return self._thread is not None
