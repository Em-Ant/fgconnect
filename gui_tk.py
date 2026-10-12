# --------------------------------------------------
# Em-Ant - 2025
# 
# A simple GUI for fgConnect using Tkinter
# --------------------------------------------------

import tkinter as tk
from tkinter import ttk
import multiprocessing as mp

from fgconnect import (
    MP_CTX,
    processReadFromFlightGear,
    processReadAIFromFlightGear,
    processWriteToLittleNavMap,
)

Process = MP_CTX.Process
Queue = MP_CTX.Queue
Value = MP_CTX.Value


def stop_processes(procs, timeout=2):
    """Wait briefly for each process, then terminate stragglers."""
    for p in procs:
        if p is None:
            continue
        p.join(timeout=timeout)
        if p.is_alive():
            p.terminate()
            p.join(timeout=1)

class MainApp(tk.Tk):

    def make_status_light(self, parent):
        c = tk.Canvas(parent, width=15, height=15, highlightthickness=0)
        c.create_oval(1, 1, 14, 14, fill="red", outline="")
        return c
    
    def __init__(self):
        super().__init__()
        self.title("fgConnect – Tkinter version")
        self.flag1 = None
        self.flag2 = None
        self.myEvtQ = Queue(maxsize=1)
        self.AIEvtQ = Queue(maxsize=1)
        self.p0 = self.p1 = self.p2 = None

        # status colours: a 15x15 canvas rectangle
        self.fg_status = tk.Canvas(self, width=15, height=15)
        self.fg_status.create_rectangle(0, 0, 15, 15, fill="red", outline="")
        self.lnm_status = tk.Canvas(self, width=15, height=15)
        self.lnm_status.create_rectangle(0, 0, 15, 15, fill="red", outline="")

        # FlightGear section
        fg_frame = ttk.LabelFrame(self, text="FlightGear")
        fg_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        ttk.Label(fg_frame, text="IP").grid(row=0, column=0)
        self.fg_ip = ttk.Entry(fg_frame, width=15)
        self.fg_ip.insert(0, "127.0.0.1")
        self.fg_ip.grid(row=0, column=1)
        ttk.Label(fg_frame, text="Port").grid(row=0, column=2)
        self.fg_port = ttk.Entry(fg_frame, width=6)
        self.fg_port.insert(0, "7755")
        self.fg_port.grid(row=0, column=3)
        ttk.Button(fg_frame, text="Start", command=self.start_fg).grid(row=0, column=4, padx=5)
        ttk.Button(fg_frame, text="Stop", command=self.stop_fg).grid(row=0, column=5)
        self.fg_status = self.make_status_light(fg_frame)
        self.fg_status.grid(row=0, column=6, padx=5, sticky="e")

        # LittleNavMap section
        lnm_frame = ttk.LabelFrame(self, text="LittleNavMap")
        lnm_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ttk.Label(lnm_frame, text="IP").grid(row=0, column=0)
        self.lnm_ip = ttk.Entry(lnm_frame, width=15)
        self.lnm_ip.insert(0, "127.0.0.1")
        self.lnm_ip.grid(row=0, column=1)
        ttk.Label(lnm_frame, text="Port").grid(row=0, column=2)
        self.lnm_port = ttk.Entry(lnm_frame, width=6)
        self.lnm_port.insert(0, "51968")
        self.lnm_port.grid(row=0, column=3)
        ttk.Button(lnm_frame, text="Start", command=self.start_lnm).grid(row=0, column=4, padx=5)
        ttk.Button(lnm_frame, text="Stop", command=self.stop_lnm).grid(row=0, column=5)
        self.lnm_status = self.make_status_light(lnm_frame)
        self.lnm_status.grid(row=0, column=6, padx=5, sticky="e")

        self.protocol("WM_DELETE_WINDOW", self.on_close)


        
    # ---- event handlers ----
    def set_status(self, canvas, color):
        canvas.itemconfig(1, fill=color)

    def start_fg(self):
        if self.flag1 is not None:
            return
        flag = Value("i", 0)
        started = []
        try:
            cfg1 = {"IP_ADDR": self.fg_ip.get(),
                    "UDP_PORT": int(self.fg_port.get()),
                    "sleepTime": 1/10.0,
                    "xmlCfgFile": "littlenavmap.xml"}
            p1 = Process(target=processReadFromFlightGear,
                         args=(flag, self.myEvtQ, cfg1),
                         daemon=True)
            p1.start()
            started.append(p1)
            cfg0 = {"IP_ADDR": self.fg_ip.get(),
                    "UDP_PORT": 5400,
                    "sleepTime": 1/2.0}
            p0 = Process(target=processReadAIFromFlightGear,
                         args=(flag, self.AIEvtQ, cfg0),
                         daemon=True)
            p0.start()
            started.append(p0)
        except Exception:
            flag.value = 1
            stop_processes(started)
            raise
        self.flag1 = flag
        self.p1, self.p0 = started
        self.set_status(self.fg_status, "green")

    def stop_fg(self):
        if self.flag1 is not None:
            self.flag1.value = 1
            stop_processes((self.p0, self.p1))
            self.p0 = self.p1 = None
            self.flag1 = None
            self.set_status(self.fg_status, "red")

    def start_lnm(self):
        if self.flag2 is not None:
            return
        flag = Value("i", 0)
        try:
            cfg = {"IP_ADDR": self.lnm_ip.get(),
                   "UDP_PORT": int(self.lnm_port.get()),
                   "sleepTime": 1/10.0}
            p2 = Process(target=processWriteToLittleNavMap,
                         args=(flag, self.myEvtQ, self.AIEvtQ, cfg),
                         daemon=True)
            p2.start()
        except Exception:
            flag.value = 1
            raise
        self.flag2 = flag
        self.p2 = p2
        self.set_status(self.lnm_status, "green")

    def stop_lnm(self):
        if self.flag2 is not None:
            self.flag2.value = 1
            stop_processes((self.p2,))
            self.p2 = None
            self.flag2 = None
            self.set_status(self.lnm_status, "red")

    def on_close(self):
        self.stop_fg()
        self.stop_lnm()
        self.destroy()


if __name__ == "__main__":
    mp.freeze_support()
    app = MainApp()
    app.mainloop()
