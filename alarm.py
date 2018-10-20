
from __future__ import print_function
from __future__ import division
import sys
import argparse
import time
import winsound
import threading
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

# add flush parameter to print if python2
if sys.version_info[:2] < (3, 3):
    old_print = print
    def print(*args, **kwargs):
        flush = kwargs.pop('flush', False)
        old_print(*args, **kwargs)
        if flush:
            file = kwargs.get('file', sys.stdout)
            # Why might file=None? IDK, but it works for print(i, file=None)
            file.flush() if file is not None else sys.stdout.flush()


class AlarmWin(object):

    def __init__(self):
        self._root = tkinter.Tk()
        self._fill_window()
        self._going_off = False

    def _fill_window(self):
        self._root.title('Alarm')
        row = tkinter.Frame(self._root)
        tkinter.Label(row, text="mins:").pack(side="left")
        self._user_mins = tkinter.Text(row, height=1, width=5)
        self._user_mins.pack(side="left")
        self._user_mins.insert(tkinter.END, "25")
        row.pack()
        row = tkinter.Frame(self._root)
        tkinter.Label(row, text="last start:").pack(side="left")
        self._started = tkinter.Label(row, text="?")
        self._started.pack(side="left")
        row.pack()
        row = tkinter.Frame(self._root)
        tkinter.Label(row, text="ticking:").pack(side="left")
        self._ticking = tkinter.Label(row, text="False")
        self._ticking.pack(side="left")
        row.pack()
        row = tkinter.Frame(self._root)
        tkinter.Button(row, text="start", command=self._start_cb).pack(side="left")
        tkinter.Button(row, text="ack", command=self.ack).pack(side="left")
        row.pack()

    def _start_cb(self):
        """Start button callback, reads minutes and starts alarm
        
        """
        user_input = self._user_mins.get("1.0", tkinter.END)
        try:
            user_input = float(user_input)
            self.start_alarm(user_input)
        except ValueError as e:
            self._started.config(text=repr(e))

    def start_alarm(self, mins):
        """Starts an alarm that will go off in :param mins: minutes
        
        :param mins: minutes until the alarm goes off
        :type mins: int
        """
        self.ack()        
        self._root.attributes('-topmost', False)
        self._ticking.config(text="True")
        self._started.config(text=time.strftime('%H:%M'))
        self._root.after(int(mins*60000), self._go_off)
        
    def _go_off(self):
        """Sets alarm off and periodically asks for attention until ack
        
        """
        self._going_off = True
        self._ticking.config(text="Ringing")
        self._root.attributes('-topmost', True)
        self.unminimize()
        def periodically_grab_attention():
            if not self._going_off:
                return
            # TODOF: do something to grab a attention
            self.unminimize()
            self._root.after(30*1000, periodically_grab_attention)
        periodically_grab_attention()

    def unminimize(self):
        """Unminimizes root window, does nothing if it's not minimized
        
        """
        self._root.wm_state('normal')  # unminimize cmd

    def ack(self):
        """Stops alarm from requiring attention
        
        """
        if self._going_off:
            self._root.attributes('-topmost', False)
            self._ticking.config(text="False")
            self._going_off = False

    def _place_window(self):
        """Places window where it ought to be
        
        """
        # get window sizes
        self._root.update()
        w = self._root.winfo_width()
        h = self._root.winfo_height()

        # get screen width and height
        ws = self._root.winfo_screenwidth() # width of the screen
        hs = self._root.winfo_screenheight() # height of the screen

        # set the dimensions of the screen
        # and where it is placed
        self._root.geometry('%dx%d+%d+%d' % (w, h, ws-w-16, hs-h-40))

    def mainloop(self):
        """Starts tkinter window loop
        
        """
        self._place_window()
        self._root.mainloop()


AlarmWin().mainloop()