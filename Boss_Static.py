from datetime import datetime, timedelta
import tkinter as tk
from threading import Timer


class Mycountdown:
    "my test countdown info"

    def __init__(self, nexttime, deltaLabel):
        self.label = deltaLabel
        self.target = nexttime

    def tick(self):
        if self.target < datetime.now():
            self.label["text"] = "-" + str(datetime.now() - self.target).split('.')[0]
            self.label["bg"] = "#ff3030"
        else:
            if (self.target-timedelta(minutes=3)) < datetime.now():
                self.label["text"] = str(self.target - datetime.now()).split('.')[0]
                self.label["bg"] = "#80ff80"
            else:
                self.label["text"] = str(self.target - datetime.now()).split('.')[0]
                self.label["bg"] = "#8080ff"

    def update_next(self, nexttime):
        self.target = nexttime


class Bossinfo:
    def __init__(self, master, id, bossname):
        self.id = id
        self.frame = tk.Frame(master=master, highlightbackground="blue", highlightthickness=2)
        self.frame.pack()
        self.check_var = tk.IntVar()
        self.check = tk.Checkbutton(self.frame, text=bossname, variable=self.check_var)
        self.check.grid(column=0, row=0, columnspan=3)

        self.timer_last = tk.Label(master=self.frame, text="last")
        self.timer_last.grid(column=1, row=1)
        self.timer_next = tk.Label(master=self.frame, text="next")
        self.timer_next.grid(column=1, row=2)
        self.timer_delta = tk.Label(master=self.frame, text="delta",font=("Consolas",12))
        self.timer_delta.grid(column=2, row=1, rowspan=2)

        self.dead = tk.Button(master=self.frame, text="Boss dead",
                              command=lambda: update_dead_time(self.id, self.timer_last, self.timer_next))
        self.dead.grid(column=0, row=1)
        self.chest = tk.Button(master=self.frame, text="Empty chest",
                               command=lambda: update_chest_time(self.id, self.timer_last, self.timer_next))
        self.chest.grid(column=0, row=2)
        timers.append(Mycountdown(datetime.now(), self.timer_delta))


def countdown():
    for ti in timers:
        ti.tick()
    Timer(1, countdown).start()


def update_dead_time(boss_index, last, next):
    t = datetime.now()
    last["text"] = t.strftime("%H:%M:%S")
    next["text"] = (t + timedelta(minutes=45)).strftime("%H:%M:%S")
    timers[boss_index].update_next(t + timedelta(minutes=45))


def update_chest_time(boss_index, last, next):
    t = datetime.now()
    last["text"] = t.strftime("%H:%M:%S")
    next["text"] = (t + timedelta(minutes=40)).strftime("%H:%M:%S")
    timers[boss_index].update_next(t + timedelta(minutes=40))


root = tk.Tk()

boss_names = ["Босс центральной комнаты", "Босс берлоги", "Босс ступенек", "Босс угла", "Босс Реки", "Босс круга"]
boss_guis = []
timers = []
bi = 0
for bname in boss_names:
    boss_guis.append(Bossinfo(root, bi, bname))
    bi += 1
#
# frame_mainroom = tk.Frame(master=root, borderwidth=2, )
# frame_mainroom.pack()
# check_mainroom_var = tk.IntVar()
# check_mainroom = tk.Checkbutton(frame_mainroom, text="Босс центральной комнаты", variable=check_mainroom_var)
# check_mainroom.grid(column=0, row=0, columnspan=3)
#
# dead_mainroom = tk.Button(master=frame_mainroom, text="Boss dead",
#                           command=lambda: update_dead_time("mainroom", timer_mainroom_last, timer_mainroom_next))
# dead_mainroom.grid(column=0, row=1)
# chest_mainroom = tk.Button(master=frame_mainroom, text="Empty chest",
#                            command=lambda: update_chest_time("mainroom", timer_mainroom_last, timer_mainroom_next))
# chest_mainroom.grid(column=0, row=2)
# timer_mainroom_last = tk.Label(master=frame_mainroom, text="last")
# timer_mainroom_last.grid(column=1, row=1)
# timer_mainroom_next = tk.Label(master=frame_mainroom, text="next")
# timer_mainroom_next.grid(column=1, row=2)
# timer_mainroom_dalta = tk.Label(master=frame_mainroom, text="delta")
# timer_mainroom_dalta.grid(column=2, row=1, rowspan=2)
# timer_mainroom = Mycountdown(datetime.now(), timer_mainroom_dalta)

countdown()

root.mainloop()
