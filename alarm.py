
from __future__ import print_function
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


parser = argparse.ArgumentParser(description='Set alarms')
parser.add_argument('mins', type=int, help='minutes till the alarm sets off')
parser.add_argument('--message', '-m', help='message')
args = parser.parse_args()


def setAlarm(mins, message):

    start = time.strftime('%H:%M')
    print(start, '->', sep=' ', end=' ', flush=True)
    time.sleep(mins*60)
    end = time.strftime('%H:%M')
    print(end)
    # print('\a')

    root = tkinter.Tk()
    root.title('Alarm')
    root.attributes('-topmost', True)

    text = "%s -> %s | %s" % (start, end, message)
    T = tkinter.Text(root, height=2, width=len(text))
    T.pack()
    T.insert(tkinter.END, text)

    # reset button
    # if clicked it's like the alarm was started again with the same parameters
    def reset():
        root.destroy()
        setAlarm(mins, message)
    resetBtn = tkinter.Button(root, text="reset", command=reset)
    resetBtn.pack()

    # beeps every 5 seconds
    no_beep = 'no_beep'
    root.setvar('beep', no_beep)
    def beep():
        def beeps(n):
            for _ in range(n):
                winsound.Beep(1000, 300)
        threading.Thread(target=beeps, args=[3]).start()
        future_beep = root.after(5000, beep)
        root.setvar('beep', future_beep)
    beep()

    # ack btn that stops/restarts beeping
    def ack():
        future_beep = root.getvar('beep')
        if future_beep != no_beep:
            root.after_cancel(future_beep)
            root.setvar('beep', no_beep)
        else:
            beep()
    ackBtn = tkinter.Button(root, text="ack", command=ack)
    ackBtn.pack()

    # get window sizes
    root.update()
    w = root.winfo_width()
    h = root.winfo_height()

    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen

    # set the dimensions of the screen
    # and where it is placed
    root.geometry('%dx%d+%d+%d' % (w, h, ws-w-16, hs-h-40))

    root.mainloop()


setAlarm(args.mins, args.message)