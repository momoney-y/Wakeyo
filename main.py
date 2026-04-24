import io
import math
import random
import struct
import sys
import threading
import time
import wave
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox

def _make_sine_wav(frequency=660, duration=0.18, volume=0.7, sample_rate=44100):
    n = int(sample_rate * duration)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n):
            t = i / sample_rate

            env = min(i / (sample_rate * 0.005 + 1),
                      (n - i) / (sample_rate * 0.01 + 1), 1.0)
            val = int(volume * env * 32767 * math.sin(2 * math.pi * frequency * t))
            frames += struct.pack('<h', val)
        w.writeframes(bytes(frames))
    return buf.getvalue()

_ALARM_WAV = _make_sine_wav(frequency=880, duration=0.22, volume=0.75)

def _play_beep(stop_event=None):
    if stop_event and stop_event.is_set():
        return
    try:
        if sys.platform == "win32":
            import winsound
            winsound.PlaySound(_ALARM_WAV, winsound.SND_MEMORY)
        else:
            sys.stdout.write('')
            sys.stdout.flush()
    except Exception:
        pass

def _stop_sound():
    try:
        if sys.platform == "win32":
            import winsound
            winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass

C = {
    "bg":          "#08090f",
    "surface":     "#0e1119",
    "surface2":    "#141822",
    "border":      "#1e2535",
    "accent":      "#00c9a7",
    "accent_dim":  "#00896f",
    "accent_glow": "#00c9a720",
    "blue":        "#3b82f6",
    "danger":      "#f43f5e",
    "danger_dim":  "#9f1239",
    "success":     "#22c55e",
    "warning":     "#f59e0b",
    "text":        "#e2e8f0",
    "text_dim":    "#64748b",
    "text_muted":  "#334155",
}

def font(size, weight="normal", family=None):
    if family is None:
        for f in ("Segoe UI", "SF Pro Display", "Helvetica Neue", "Helvetica"):
            family = f
            break
    return (family, size, weight)

MONO = ("Courier New", 52, "bold")

WORD = {
    "hello":    "Used for greeting",
    "world":    "Description of the universe",
    "python":   "A popular programming language",
    "alarm":    "Wakes you up in the morning",
    "clock":    "An instrument that shows time",
    "computer": "Electronic device for processing data",
    "keyboard": "Device used for typing",
    "mouse":    "Pointing device for computers",
    "monitor":  "Display screen for computers",
    "internet": "Global network connecting computers",
    "coffee":   "Beverage made from roasted beans",
    "music":    "Art form using sound and rhythm",
    "book":     "Collection of written pages",
    "phone":    "Device for communication",
    "weather":  "State of the atmosphere",
}

keys_list   = list(WORD.keys())
values_list = list(WORD.values())

def rounded_rect(canvas, x1, y1, x2, y2, r=12, **kw):
    pts = [
        x1+r, y1,  x2-r, y1,
        x2,   y1,  x2,   y1+r,
        x2,   y2-r,x2,   y2,
        x2-r, y2,  x1+r, y2,
        x1,   y2,  x1,   y2-r,
        x1,   y1+r,x1,   y1,
        x1+r, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)

class Card(Frame):
    def __init__(self, parent, radius=14, bg=None, border=True, **kw):
        bg_color = bg or C["surface"]
        super().__init__(parent, bg=C["bg"], **kw)
        self._canvas = Canvas(self, bg=C["bg"], highlightthickness=0)
        self._canvas.place(relwidth=1, relheight=1)
        self._radius = radius
        self._bg_color = bg_color
        self._border = border
        self._canvas.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        w, h = self._canvas.winfo_width(), self._canvas.winfo_height()
        self._canvas.delete("bg")
        if self._border:
            rounded_rect(self._canvas, 1, 1, w-1, h-1, r=self._radius,
                         fill=C["border"], outline="", tags="bg")
        rounded_rect(self._canvas, 2, 2, w-2, h-2, r=self._radius-1,
                     fill=self._bg_color, outline="", tags="bg")

class ModernButton(Frame):
    def __init__(self, parent, text="", command=None,
                 bg=C["accent"], fg=C["bg"], hover=C["accent_dim"],
                 icon="", width=140, height=38, radius=10, **kw):
        kw.pop("highlightthickness", None)
        super().__init__(parent, width=width, height=height,
                         bg=parent.cget("bg"), **kw)
        self.pack_propagate(False)

        self._cv = Canvas(self, width=width, height=height,
                          bg=parent.cget("bg"), highlightthickness=0)
        self._cv.place(x=0, y=0, width=width, height=height)

        self._text    = icon + (" " if icon else "") + text
        self._command = command
        self._bg      = bg
        self._hover   = hover
        self._fg      = fg
        self._radius  = radius
        self._bw      = width
        self._bh      = height
        self._state   = NORMAL

        self._draw(bg)

        for w in (self, self._cv):
            w.bind("<Enter>",           self._on_enter)
            w.bind("<Leave>",           self._on_leave)
            w.bind("<ButtonPress-1>",   self._on_press)
            w.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self, color):
        self._cv.delete("all")
        rounded_rect(self._cv, 0, 0, self._bw, self._bh,
                     r=self._radius, fill=color, outline="")
        self._cv.create_text(self._bw // 2, self._bh // 2, text=self._text,
                             fill=self._fg, font=font(10, "bold"))

    def _on_enter(self, _):
        if self._state == NORMAL:
            self._draw(self._hover)
            self._cv.config(cursor="hand2")

    def _on_leave(self, _):
        if self._state == NORMAL:
            self._draw(self._bg)
            self._cv.config(cursor="")

    def _on_press(self, _):
        if self._state == NORMAL:
            self._draw(self._bg)

    def _on_release(self, _):
        if self._state == NORMAL:
            self._draw(self._hover)
            if self._command:
                self._command()

    def config_state(self, state):
        self._state = state
        if state == DISABLED:
            dim = _blend(self._bg, C["surface"], 0.55)
            self._draw(dim)
            self._cv.config(cursor="")
        else:
            self._draw(self._bg)

def _blend(hex1, hex2, t):
    r1,g1,b1 = int(hex1[1:3],16), int(hex1[3:5],16), int(hex1[5:7],16)
    r2,g2,b2 = int(hex2[1:3],16), int(hex2[3:5],16), int(hex2[5:7],16)
    r = int(r1 + (r2-r1)*t)
    g = int(g1 + (g2-g1)*t)
    b = int(b1 + (b2-b1)*t)
    return f"#{r:02x}{g:02x}{b:02x}"

class Divider(Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, height=1, bg=C["border"], **kw)

class ModernEntry(Entry):
    def __init__(self, parent, placeholder="", **kw):
        self._ph = placeholder
        self._ph_active = False
        super().__init__(parent,
            bg=C["surface2"], fg=C["text"],
            insertbackground=C["accent"],
            relief=FLAT, bd=0,
            highlightthickness=1,
            highlightbackground=C["border"],
            highlightcolor=C["accent"],
            font=font(12),
            **kw)
        if placeholder:
            self._show_placeholder()
            self.bind("<FocusIn>",  self._clear_placeholder)
            self.bind("<FocusOut>", self._restore_placeholder)

    def _show_placeholder(self):
        self.insert(0, self._ph)
        self.config(fg=C["text_dim"])
        self._ph_active = True

    def _clear_placeholder(self, _=None):
        if self._ph_active:
            self.delete(0, END)
            self.config(fg=C["text"])
            self._ph_active = False

    def _restore_placeholder(self, _=None):
        if not self.get():
            self._show_placeholder()

    def real_value(self):
        return "" if self._ph_active else self.get().strip()

class ModernSpinbox(Frame):
    def __init__(self, parent, from_=0, to=23, label="", value=None, **kw):
        super().__init__(parent, bg=C["surface2"], **kw)
        self._from = from_
        self._to   = to
        self._var  = IntVar(value=value if value is not None else from_)

        Label(self, text=label, font=font(9), bg=C["surface2"],
              fg=C["text_dim"]).pack(anchor=W, padx=8, pady=(6,0))

        row = Frame(self, bg=C["surface2"])
        row.pack(padx=6, pady=(0,6))

        self._down = Canvas(row, width=22, height=22, bg=C["surface2"],
                            highlightthickness=0, cursor="hand2")
        self._down.pack(side=LEFT, padx=(0,4))
        self._draw_arrow(self._down, "left")
        self._down.bind("<ButtonRelease-1>", lambda _: self._step(-1))

        self._label = Label(row, textvariable=self._var,
                            font=font(18, "bold"),
                            bg=C["surface2"], fg=C["text"], width=3,
                            anchor=CENTER)
        self._label.pack(side=LEFT)

        self._up = Canvas(row, width=22, height=22, bg=C["surface2"],
                          highlightthickness=0, cursor="hand2")
        self._up.pack(side=LEFT, padx=(4,0))
        self._draw_arrow(self._up, "right")
        self._up.bind("<ButtonRelease-1>", lambda _: self._step(1))

        for w in (self._label, self._down, self._up, row, self):
            w.bind("<MouseWheel>", self._on_wheel)

    def _draw_arrow(self, canvas, direction):
        canvas.delete("all")
        canvas.create_oval(1,1,21,21, fill=C["surface"], outline=C["border"])
        if direction == "right":
            canvas.create_polygon(8,6, 15,11, 8,16, fill=C["accent"], outline="")
        else:
            canvas.create_polygon(14,6, 7,11, 14,16, fill=C["accent"], outline="")

    def _step(self, delta):
        v = (self._var.get() + delta - self._from) % (self._to - self._from + 1) + self._from
        self._var.set(v)

    def _on_wheel(self, event):
        self._step(1 if event.delta > 0 else -1)

    def get(self):
        return self._var.get()

class AddWordDialog:
    def __init__(self, parent):
        self.dialog = Toplevel(parent)
        self.dialog.title("Add New Word")
        self.dialog.geometry("420x300")
        self.dialog.configure(bg=C["bg"])
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self._center(420, 300)
        self._build()

    def _center(self, w, h):
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth()  - w) // 2
        y = (self.dialog.winfo_screenheight() - h) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def _build(self):
        pad = Frame(self.dialog, bg=C["bg"])
        pad.pack(fill=BOTH, expand=True, padx=24, pady=24)

        Label(pad, text="Add New Word", font=font(18, "bold"),
              bg=C["bg"], fg=C["text"]).pack(anchor=W)
        Label(pad, text="Expand the puzzle vocabulary",
              font=font(10), bg=C["bg"], fg=C["text_dim"]).pack(anchor=W, pady=(2,18))

        Label(pad, text="WORD", font=font(8, "bold"),
              bg=C["bg"], fg=C["text_dim"]).pack(anchor=W)
        self.word_entry = ModernEntry(pad, placeholder="e.g. galaxy", width=36)
        self.word_entry.pack(fill=X, ipady=8, pady=(3,12))

        Label(pad, text="DESCRIPTION", font=font(8, "bold"),
              bg=C["bg"], fg=C["text_dim"]).pack(anchor=W)
        self.desc_entry = ModernEntry(pad, placeholder="e.g. A system of stars", width=36)
        self.desc_entry.pack(fill=X, ipady=8, pady=(3,20))

        btns = Frame(pad, bg=C["bg"])
        btns.pack(fill=X)
        ModernButton(btns, text="Add Word", command=self._add,
                     bg=C["accent"], fg=C["bg"], hover=C["accent_dim"],
                     icon="✦", width=130, height=38).pack(side=LEFT)
        ModernButton(btns, text="Cancel", command=self.dialog.destroy,
                     bg=C["surface2"], fg=C["text_dim"], hover=C["border"],
                     width=110, height=38).pack(side=LEFT, padx=(10,0))

    def _add(self):
        word = self.word_entry.real_value().lower()
        desc = self.desc_entry.real_value()
        if not word or not desc:
            messagebox.showerror("Missing Fields", "Please enter both word and description.", parent=self.dialog)
            return
        if word in WORD:
            messagebox.showerror("Duplicate", f"'{word}' already exists.", parent=self.dialog)
            return
        WORD[word] = desc
        global keys_list, values_list
        keys_list   = list(WORD.keys())
        values_list = list(WORD.values())
        messagebox.showinfo("Added!", f"'{word}' is now part of the puzzle set.", parent=self.dialog)
        self.dialog.destroy()

class AlarmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Alarm")
        self.root.configure(bg=C["bg"])
        self.root.resizable(False, False)

        self.alarm_running = False
        self.alarm_thread  = None
        self.volume_increment      = 1.0
        self.current_alarm_window  = None
        self._alarm_target = None
        self._alarm_cancel = threading.Event()
        self._sound_stop   = threading.Event()

        self._build_ui()
        self._center(480, 540)

    def _center(self, w, h):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        self.root.geometry("480x590")
        outer = Frame(self.root, bg=C["bg"])
        outer.pack(fill=BOTH, expand=True, padx=24, pady=24)

        self._build_header(outer)
        self._build_clock(outer)
        self._build_alarm_setter(outer)
        self._build_word_panel(outer)
        self._build_status(outer)

    def _build_header(self, parent):
        row = Frame(parent, bg=C["bg"])
        row.pack(fill=X, pady=(0, 20))

        dot = Canvas(row, width=10, height=10, bg=C["bg"], highlightthickness=0)
        dot.pack(side=LEFT, padx=(0,8), pady=6)
        dot.create_oval(0, 0, 10, 10, fill=C["accent"], outline="")

        Label(row, text="SMART ALARM", font=font(13, "bold"),
              bg=C["bg"], fg=C["text"]).pack(side=LEFT)

    def _build_clock(self, parent):
        card = Card(parent, radius=16, bg=C["surface"])
        card.pack(fill=X, pady=(0,14))

        inner = Frame(card, bg=C["surface"])
        inner.pack(pady=22, padx=28)

        stripe = Canvas(inner, width=36, height=3, bg=C["surface"], highlightthickness=0)
        stripe.pack(anchor=W, pady=(0,10))
        stripe.create_rectangle(0, 0, 36, 3, fill=C["accent"], outline="")

        Label(inner, text="CURRENT TIME", font=font(8, "bold"),
              bg=C["surface"], fg=C["text_dim"]).pack(anchor=W)

        self.time_label = Label(inner, text="", font=MONO,
                                bg=C["surface"], fg=C["text"])
        self.time_label.pack(anchor=W, pady=(4,2))

        self.date_label = Label(inner, text="", font=font(10),
                                bg=C["surface"], fg=C["text_dim"])
        self.date_label.pack(anchor=W)

        self._update_clock()

    def _build_alarm_setter(self, parent):
        card = Card(parent, radius=16, bg=C["surface"])
        card.pack(fill=X, pady=(0,14))

        inner = Frame(card, bg=C["surface"])
        inner.pack(padx=28, pady=20)

        Label(inner, text="SET ALARM", font=font(8, "bold"),
              bg=C["surface"], fg=C["text_dim"]).pack(anchor=W, pady=(0,14))

        spin_row = Frame(inner, bg=C["surface"])
        spin_row.pack(anchor=W)

        _now = datetime.now()

        h_card = Card(spin_row, radius=10, bg=C["surface2"], border=False)
        h_card.pack(side=LEFT, ipadx=8, ipady=4)
        self.hour_spin = ModernSpinbox(h_card, from_=0, to=23, label="HOUR",
                                       value=_now.hour)
        self.hour_spin.pack(padx=2, pady=2)

        Label(spin_row, text=":", font=font(28, "bold"),
              bg=C["surface"], fg=C["text_dim"]).pack(side=LEFT, padx=12)

        m_card = Card(spin_row, radius=10, bg=C["surface2"], border=False)
        m_card.pack(side=LEFT, ipadx=8, ipady=4)
        self.min_spin = ModernSpinbox(m_card, from_=0, to=59, label="MIN",
                                      value=_now.minute)
        self.min_spin.pack(padx=2, pady=2)

        Divider(inner).pack(fill=X, pady=18)

        btn_row = Frame(inner, bg=C["surface"])
        btn_row.pack(anchor=W)

        self.set_btn = ModernButton(btn_row, text="Set Alarm",
                                   command=self.set_alarm, icon="⏰",
                                   bg=C["accent"], fg=C["bg"],
                                   hover=C["accent_dim"], width=150, height=25)
        self.set_btn.pack(side=LEFT)

        self.stop_btn = ModernButton(btn_row, text="Cancel",
                                    command=self.stop_alarm, icon="✕",
                                    bg=C["danger"], fg=C["text"],
                                    hover=C["danger_dim"], width=150, height=25)
        self.stop_btn.pack(side=LEFT, padx=(12,0))
        self.stop_btn.config_state(DISABLED)

    def _build_word_panel(self, parent):
        card = Card(parent, radius=16, bg=C["surface"])
        card.pack(fill=X, pady=(0,14))

        inner = Frame(card, bg=C["surface"])
        inner.pack(padx=28, pady=18, fill=X)

        row = Frame(inner, bg=C["surface"])
        row.pack(fill=X)

        left = Frame(row, bg=C["surface"])
        left.pack(side=LEFT, fill=Y)

        Label(left, text="PUZZLE WORDS", font=font(8, "bold"),
              bg=C["surface"], fg=C["text_dim"]).pack(anchor=W)

        self.word_count = Label(left, text=f"{len(WORD)} words in the bank",
                                font=font(11), bg=C["surface"], fg=C["text"])
        self.word_count.pack(anchor=W, pady=(4,0))

        ModernButton(row, text="Add Word", command=self._open_add_word,
                     icon="＋", bg=C["surface2"], fg=C["text"],
                     hover=C["border"], width=120, height=34).pack(side=RIGHT)

    def _build_status(self, parent):
        self.status_bar = Label(parent, text="● Ready to set an alarm",
                                font=font(9), bg=C["bg"], fg=C["accent"])
        self.status_bar.pack(anchor=W, pady=(4,0))

        self.countdown_label = Label(parent, text="",
                                     font=font(9), bg=C["bg"], fg=C["text_dim"])
        self.countdown_label.pack(anchor=W, pady=(2,0))
        self._update_countdown()

    def _update_clock(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("%H:%M:%S"))
        self.date_label.config(text=now.strftime("%A, %d %B %Y"))
        self.root.after(1000, self._update_clock)

    def _update_countdown(self):
        if self.alarm_running:
            self.countdown_label.config(text="")
        elif hasattr(self, '_alarm_target') and self._alarm_target:
            now = datetime.now()
            diff = int((self._alarm_target - now).total_seconds())
            if diff > 0:
                h = diff // 3600
                m = (diff % 3600) // 60
                s = diff % 60
                self.countdown_label.config(
                    text=f"⏱  {h:02d}:{m:02d}:{s:02d} until alarm",
                    fg=C["text_dim"])
            else:
                self.countdown_label.config(text="")
                self._alarm_target = None
        else:
            self.countdown_label.config(text="")
        self.root.after(1000, self._update_countdown)

    def _set_status(self, text, color=C["accent"]):
        self.status_bar.config(text=text, fg=color)

    def _open_add_word(self):
        AddWordDialog(self.root)
        self.word_count.config(text=f"{len(WORD)} words in the bank")

    def set_alarm(self):
        try:
            hour   = self.hour_spin.get()
            minute = self.min_spin.get()
        except ValueError:
            self._set_status("✖ Invalid time value", C["danger"])
            return

        now = datetime.now()
        alarm_dt = datetime(now.year, now.month, now.day, hour, minute)
        if alarm_dt <= now:
            alarm_dt = alarm_dt.replace(day=now.day + 1)

        self._alarm_target = alarm_dt
        self._alarm_cancel.clear()
        self._sound_stop.clear()
        self._set_status(f"⏰ Alarm set for {hour:02d}:{minute:02d}", C["accent"])
        self.set_btn.config_state(DISABLED)
        self.stop_btn.config_state(NORMAL)

        self.alarm_thread = threading.Thread(
            target=self._wait_for_alarm, args=((hour, minute),), daemon=True
        )
        self.alarm_thread.start()

    def stop_alarm(self):
        self._alarm_cancel.set()
        self._sound_stop.set()
        self.alarm_running = False
        self._alarm_target = None
        _stop_sound()
        if self.current_alarm_window:
            try:
                self.current_alarm_window.destroy()
            except Exception:
                pass
            self.current_alarm_window = None
        self._set_status("● Alarm cancelled", C["text_dim"])
        self.countdown_label.config(text="")
        self.set_btn.config_state(NORMAL)
        self.stop_btn.config_state(DISABLED)

    def _wait_for_alarm(self, alarm_time):
        while not self.alarm_running and not self._alarm_cancel.is_set():
            now = datetime.now()
            if (now.hour, now.minute) == alarm_time:
                self.alarm_running = True
                self.root.after(0, self._trigger_alarm)
                break
            time.sleep(1)

    def _trigger_alarm(self):
        self._sound_stop.clear()
        self.volume_increment = 1.0
        self.stop_btn.config_state(NORMAL)
        self._set_status("🔔 ALARM RINGING — solve the puzzle!", C["danger"])

        win = Toplevel(self.root)
        self.current_alarm_window = win
        win.title("Wake Up!")
        win.geometry("460x500")
        win.configure(bg=C["bg"])
        win.resizable(False, False)
        win.attributes("-topmost", True)

        win.update_idletasks()
        x = (win.winfo_screenwidth()  - 460) // 2
        y = (win.winfo_screenheight() - 500) // 2
        win.geometry(f"+{x}+{y}")

        self._build_alarm_ui(win)
        self._show_new_puzzle()
        self._play_alarm_sound()

    def _build_alarm_ui(self, win):
        outer = Frame(win, bg=C["bg"])
        outer.pack(fill=BOTH, expand=True, padx=24, pady=24)

        hdr = Frame(outer, bg=C["bg"])
        hdr.pack(fill=X, pady=(0,16))

        self._alarm_dot = Canvas(hdr, width=12, height=12, bg=C["bg"],
                                 highlightthickness=0)
        self._alarm_dot.pack(side=LEFT, padx=(0,8), pady=4)
        self._alarm_dot.create_oval(0,0,12,12, fill=C["danger"], outline="", tags="dot")

        Label(hdr, text="WAKE  UP", font=font(16, "bold"),
              bg=C["bg"], fg=C["text"]).pack(side=LEFT)

        prog_card = Card(outer, radius=10, bg=C["surface"])
        prog_card.pack(fill=X, pady=(0,14))

        prog_inner = Frame(prog_card, bg=C["surface"])
        prog_inner.pack(padx=18, pady=14, fill=X)

        row = Frame(prog_inner, bg=C["surface"])
        row.pack(fill=X)
        Label(row, text="ALARM INTENSITY", font=font(8, "bold"),
              bg=C["surface"], fg=C["text_dim"]).pack(side=LEFT)
        self._level_label = Label(row, text="Level 1", font=font(8, "bold"),
                                  bg=C["surface"], fg=C["danger"])
        self._level_label.pack(side=RIGHT)

        prog_bg = Canvas(prog_inner, height=6, bg=C["surface2"],
                         highlightthickness=0)
        prog_bg.pack(fill=X, pady=(8,0))
        self._prog_bg  = prog_bg
        self._prog_bar_id = None
        prog_bg.bind("<Configure>", lambda e: self._redraw_progress())
        self._prog_value = 0.0
        self._prog_max   = 5.0

        puzzle_card = Card(outer, radius=14, bg=C["surface"])
        puzzle_card.pack(fill=X, pady=(0,14))

        puz_inner = Frame(puzzle_card, bg=C["surface"])
        puz_inner.pack(padx=22, pady=20, fill=X)

        Label(puz_inner, text="PUZZLE", font=font(8, "bold"),
              bg=C["surface"], fg=C["text_dim"]).pack(anchor=W)

        self._puzzle_clue = Label(puz_inner, text="", font=font(13),
                                  bg=C["surface"], fg=C["text"],
                                  wraplength=370, justify=LEFT)
        self._puzzle_clue.pack(anchor=W, pady=(6,14))

        Divider(puz_inner).pack(fill=X, pady=(0,14))

        Label(puz_inner, text="YOUR ANSWER", font=font(8, "bold"),
              bg=C["surface"], fg=C["text_dim"]).pack(anchor=W)

        self._answer_entry = ModernEntry(puz_inner, placeholder="Type the word...", width=32)
        self._answer_entry.pack(fill=X, ipady=9, pady=(4,0))
        self._answer_entry.bind("<Return>", lambda e: self._check_puzzle(self.current_alarm_window))

        self._puzzle_feedback = Label(puz_inner, text="", font=font(10),
                                      bg=C["surface"], fg=C["text_dim"])
        self._puzzle_feedback.pack(anchor=W, pady=(8,0))

        btn_row = Frame(outer, bg=C["bg"])
        btn_row.pack(fill=X)

        ModernButton(btn_row, text="Submit", command=lambda: self._check_puzzle(self.current_alarm_window),
                     icon="↵", bg=C["accent"], fg=C["bg"], hover=C["accent_dim"],
                     width=155, height=42).pack(side=LEFT)

        ModernButton(btn_row, text="Hint", command=self._show_hint,
                     icon="💡", bg=C["surface2"], fg=C["text_dim"],
                     hover=C["border"], width=100, height=42).pack(side=LEFT, padx=(10,0))

        self._blink_dot()

    def _blink_dot(self):
        if not self.alarm_running or not self.current_alarm_window:
            return
        colors = [C["danger"], C["bg"]]
        current = self._alarm_dot.itemcget("dot", "fill")
        next_c = colors[0] if current != colors[0] else colors[1]
        self._alarm_dot.itemconfig("dot", fill=next_c)
        self.current_alarm_window.after(500, self._blink_dot)

    def _redraw_progress(self):
        w = self._prog_bg.winfo_width()
        h = self._prog_bg.winfo_height()
        self._prog_bg.delete("all")
        self._prog_bg.create_rectangle(0, 0, w, h, fill=C["surface"], outline="")
        fill_w = int(w * min(self._prog_value / self._prog_max, 1.0))
        if fill_w > 0:
            ratio = self._prog_value / self._prog_max
            if ratio < 0.5:
                color = _blend(C["accent"], C["warning"], ratio * 2)
            else:
                color = _blend(C["warning"], C["danger"], (ratio - 0.5) * 2)
            self._prog_bg.create_rectangle(0, 0, fill_w, h, fill=color, outline="")

    def _show_new_puzzle(self):
        idx = random.randint(0, len(keys_list) - 1)
        self.current_word = keys_list[idx]
        self.current_desc = values_list[idx]
        self._puzzle_clue.config(text=f'"{self.current_desc}"')
        if hasattr(self, "_answer_entry"):
            self._answer_entry._clear_placeholder()
            self._answer_entry.delete(0, END)
            self._answer_entry._restore_placeholder()
            self._puzzle_feedback.config(text="")
        self._answer_entry.focus()

    def _show_hint(self):
        word = self.current_word
        hint = f"Starts with  « {word[0].upper()} »  ·  {len(word)} letters"
        messagebox.showinfo("Hint", hint, parent=self.current_alarm_window)

    def _check_puzzle(self, window):
        guess = self._answer_entry.real_value().lower()
        if guess == self.current_word:
            self._sound_stop.set()
            self.alarm_running = False
            _stop_sound()
            self._puzzle_feedback.config(text="✓ Correct — alarm dismissed!", fg=C["success"])
            self._set_status("✓ Well done! Alarm dismissed.", C["success"])
            window.after(800, window.destroy)
            self.set_btn.config_state(NORMAL)
            self.stop_btn.config_state(DISABLED)
        else:
            self.volume_increment = min(self.volume_increment + 0.5, self._prog_max)
            self._prog_value = self.volume_increment
            self._redraw_progress()
            level = int(self.volume_increment)
            self._level_label.config(text=f"Level {level}")
            self._puzzle_feedback.config(
                text=f"✖ Wrong answer — intensity rising to level {level}",
                fg=C["danger"])
            self._answer_entry._clear_placeholder()
            self._answer_entry.delete(0, END)
            self._answer_entry._restore_placeholder()
            self._answer_entry.focus()

    def _play_alarm_sound(self):
        if not self.alarm_running or self._sound_stop.is_set():
            return
        threading.Thread(target=_play_beep, args=(self._sound_stop,), daemon=True).start()
        if self.alarm_running and not self._sound_stop.is_set():
            delay = max(0.12, 0.55 / self.volume_increment)
            threading.Timer(delay, self._play_alarm_sound).start()

if __name__ == "__main__":
    root = Tk()
    AlarmApp(root)
    root.mainloop()
