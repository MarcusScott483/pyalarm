from __future__ import print_function
from __future__ import division
import sys
import time
import os
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


# absolute script directory path
abs_dir = os.path.dirname(os.path.abspath(__file__))


class AlarmWin(object):

    def __init__(self):
        self._root = tkinter.Tk()
        self._root.iconbitmap(os.path.join(abs_dir, "data", "alarm.ico"))
        self._default_bg = self._root.cget('bg')
        self._afters = set()
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
        self._state = tkinter.Label(self._root, text="idle")
        self._state.pack()
        row = tkinter.Frame(self._root)
        self._minimize_chk_var = tkinter.IntVar()
        tkinter.Button(row, text="start", command=self._start_cb).pack(side="left")
        tkinter.Button(row, text="ack", command=self.ack).pack(side="left")
        tkinter.Checkbutton(row, text="auto min", variable=self._minimize_chk_var).pack(side="left")
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

    def _schedule(self, ms, func, *args):
        """Schedules :param func: to be executed after :param ms: milliseconds, registering it in ._afters
        
        :param ms: milliseconds of delay
        :type ms: int
        :param func: function to be executed
        :type func: callable

        :return: scheduling identifier
        :rtype: str
        """
        def wrapper(*args):
            func(*args)
            self._afters.remove(after_id)
        after_id = self._root.after(ms, wrapper, *args)
        self._afters.add(after_id)
        return after_id

    def _unschedule(self, after_id=None):
        """Unschedules function with given id, by default unschedules all functions
        
        :param after_id: function id to be unscheduled, defaults to None (i.e. all functions)
        :param after_id: str, optional
        """
        if after_id is None:
            for id_ in self._afters:
                self._root.after_cancel(id_)
            self._afters.clear()
        else:
            self._root.after_cancel(after_id)
            self._afters.discard(id_)

    def start_alarm(self, mins):
        """Starts an alarm that will go off in :param mins: minutes, if checkbox is ticked minimizes window
        
        :param mins: minutes until the alarm goes off
        :type mins: int
        """
        self.ack()        
        # don't force window to be topmost anymore
        self._root.attributes('-topmost', False)
        # update state text
        self._state.config(text="ticking")
        # update start time
        self._started.config(text=time.strftime('%H:%M'))

        # minimize if checkbox ticked
        if self._minimize_chk_var.get() == 1:
            self.minimize()

        # schedule going off
        self._schedule(int(mins*60000), self._go_off)
        
    def _go_off(self):
        """Sets alarm off and periodically asks for attention until ack
        
        """
        self._going_off = True
        self._state.config(text="ringing")
        self._root.attributes('-topmost', True)
        self.unminimize()
        def periodically_grab_attention():
            self.unminimize()
            self._root.config(background="orange")
            for i in range(3):
                self._schedule(i*1000 + 500, lambda: self._root.config(background=self._default_bg))
                self._schedule(i*1000 + 1000, lambda: self._root.config(background="orange"))
            self._schedule(30*1000, periodically_grab_attention)
        periodically_grab_attention()

    def minimize(self):
        """Minimizes the window
        
        """
        self._root.wm_state('iconic')  # minimize cmd

    def unminimize(self):
        """Unminimizes root window, does nothing if it's not minimized
        
        """
        self._root.wm_state('normal')  # unminimize cmd

    def ack(self):
        """Stops alarm from requiring attention
        
        """
        self._unschedule()
        self._root.attributes('-topmost', False)
        self._state.config(text="idle")
        self._root.config(background=self._default_bg)
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
