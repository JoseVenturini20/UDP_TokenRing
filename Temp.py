import time
import threading
import logging
import os
import platform

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import threading
import os
import platform
import time

class Temp:
    """
    A timer class that counts down from a specified number of seconds.
    """
    def __init__(self, seconds, alignment=10, text="", update_callback=None):
        self.__init_seconds = seconds
        self.__seconds = seconds
        self.__thread = None
        self.__stop_event = threading.Event()
        self.__alignment = alignment
        self.__text = text
        self.__update_callback = update_callback
        self.__callback = None

    def __run(self):
        while self.__seconds and not self.__stop_event.is_set():
            self.__test = False
            # self._clear_terminal()
            mins, secs = divmod(self.__seconds, 60)
            timeformat = '{: >{align}}'.format(f'{self.__text}{mins:02d}:{secs:02d}', align=self.__alignment)
            if self.__update_callback:
                self.__update_callback(timeformat, self)
            time.sleep(1)
            self.__seconds -= 1
        timeformat = '{: >{align}}'.format(f'{self.__text}---', align=self.__alignment)
        self.__update_callback(timeformat, self)
        if self.__stop_event.is_set():
            self.__stop_event.clear()
        else:
            if self.__callback:
                self.__callback()
            self.__seconds = self.__init_seconds 

        self.__thread = None

    def _clear_terminal(self):
        os.system('cls' if platform.system() == 'Windows' else 'clear')

    def start(self, callback=None):
        """
        Starts the timer. If the timer is already running, it will be stopped and restarted.
        """
        self.__callback = callback
        self.__seconds = self.__init_seconds
        self.__stop_event.clear()

        if (self.__thread and self.__thread.is_alive()):
            print("Timer is already running")
            self.stop()

        self.__thread = threading.Thread(target=self.__run)
        self.__thread.start()


    def stop(self):
        """
        Stops the timer and resets the remaining seconds to the initial value.
        """
        print(f"Stopping timer. Initial seconds: {self.__init_seconds}")
        self.__seconds = self.__init_seconds 
        print(f"Timer reset. Seconds now: {self.__seconds}")
        self.__thread = None
        self.__stop_event.set()


    def is_running(self):
        """
        Returns True if the timer is currently running, False otherwise.
        """
        return self.__thread is not None and self.__thread.is_alive()

    @property
    def seconds(self):
        """
        Returns the number of seconds remaining in the timer.
        """
        return self.__seconds

