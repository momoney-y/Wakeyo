import random
import threading
import time
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox
import tkinter.simpledialog
try:
    from playsound import playsound
    HAS_PLAYSOUND = True
except ImportError:
    HAS_PLAYSOUND = False

WORD = {
    "hello": "Used for greeting",
    "world": "Description of universe",
    "python": "A programming language",
    "alarm": "Wakes you up in the morning",
    "clock": "Shows you the time",
    "computer": "Electronic device for processing data",
    "keyboard": "Device used for typing",
    "mouse": "Pointing device for computers",
    "monitor": "Display screen for computers",
    "internet": "Global network connecting computers",
    "coffee": "Beverage made from roasted beans",
    "music": "Art form using sound and rhythm",
    "book": "Collection of written pages",
    "phone": "Device for communication",
    "weather": "State of the atmosphere"
}

keys_list = list(WORD.keys())
values_list = list(WORD.values())

class AddWordDialog:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = Toplevel(parent)
        self.dialog.title("Add New Word")
        self.dialog.geometry("400x250")
        self.dialog.configure(bg="#2c3e50")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.dialog.resizable(False, False)

        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (250 // 2)
        self.dialog.geometry(f"+{x}+{y}")

        Label(self.dialog, text="Add New Word", font=("Arial", 18, "bold"),
              bg="#2c3e50", fg="white").pack(pady=15)

        frame = Frame(self.dialog, bg="#2c3e50")
        frame.pack(pady=20)

        Label(frame, text="Word:", font=("Arial", 12), bg="#2c3e50", fg="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.word_entry = Entry(frame, font=("Arial", 12), width=20)
        self.word_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(frame, text="Description:", font=("Arial", 12), bg="#2c3e50", fg="white").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.desc_entry = Entry(frame, font=("Arial", 12), width=20)
        self.desc_entry.grid(row=1, column=1, padx=10, pady=10)

        button_frame = Frame(self.dialog, bg="#2c3e50")
        button_frame.pack(pady=20)

        Button(button_frame, text="Add", font=("Arial", 12), command=self.add_word,
               bg="#27ae60", fg="white", padx=20).pack(side=LEFT, padx=10)
        Button(button_frame, text="Cancel", font=("Arial", 12), command=self.dialog.destroy,
               bg="#e74c3c", fg="white", padx=20).pack(side=LEFT, padx=10)

    def add_word(self):
        word = self.word_entry.get().strip().lower()
        description = self.desc_entry.get().strip()

        if not word or not description:
            messagebox.showerror("Error", "Please enter both word and description!")
            return

        if word in WORD:
            messagebox.showerror("Error", "This word already exists!")
            return

        WORD[word] = description
        global keys_list, values_list
        keys_list = list(WORD.keys())
        values_list = list(WORD.values())

        messagebox.showinfo("Success", f"Word '{word}' added successfully!")
        self.dialog.destroy()

class AlarmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Alarm Clock")
        self.root.geometry("500x450")
        self.root.configure(bg="#1a1a2e")

        self.center_window()

        self.alarm_running = False
        self.alarm_thread = None
        self.volume_increment = 1.0
        self.current_alarm_window = None

        self.create_widgets()

    def center_window(self):
        self.root.update_idletasks()
        width = 500
        height = 450
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        title_frame = Frame(self.root, bg="#1a1a2e")
        title_frame.pack(pady=20)

        title = Label(title_frame, text="⏰ SMART ALARM CLOCK",
                     font=("Arial", 24, "bold"), bg="#1a1a2e", fg="#e94560")
        title.pack()

        subtitle = Label(title_frame, text="Wake up smarter!",
                        font=("Arial", 10), bg="#1a1a2e", fg="#a0a0a0")
        subtitle.pack()

        time_frame = Frame(self.root, bg="#16213e", relief=RAISED, bd=2)
        time_frame.pack(pady=20, padx=40, fill=X)

        self.time_label = Label(time_frame, text="", font=("DS-Digital", 60),
                               bg="#16213e", fg="#0f3460")
        self.time_label.pack(pady=20)
        self.update_clock()

        alarm_frame = LabelFrame(self.root, text="Set Alarm", font=("Arial", 12, "bold"),
                                 bg="#1a1a2e", fg="white", padx=20, pady=10)
        alarm_frame.pack(pady=10, padx=40, fill=X)

        time_input_frame = Frame(alarm_frame, bg="#1a1a2e")
        time_input_frame.pack(pady=10)

        Label(time_input_frame, text="Hour:", font=("Arial", 12),
              bg="#1a1a2e", fg="white").pack(side=LEFT, padx=5)

        self.hour_spin = Spinbox(time_input_frame, from_=0, to=23, width=5,
                                 font=("Arial", 14), format="%02.0f")
        self.hour_spin.pack(side=LEFT, padx=5)

        Label(time_input_frame, text="Minute:", font=("Arial", 12),
              bg="#1a1a2e", fg="white").pack(side=LEFT, padx=5)

        self.min_spin = Spinbox(time_input_frame, from_=0, to=59, width=5,
                                font=("Arial", 14), format="%02.0f")
        self.min_spin.pack(side=LEFT, padx=5)

        button_frame = Frame(alarm_frame, bg="#1a1a2e")
        button_frame.pack(pady=15)

        self.set_button = Button(button_frame, text="Set Alarm", font=("Arial", 12, "bold"),
                                command=self.set_alarm, bg="#e94560", fg="white",
                                padx=20, pady=5, cursor="hand2")
        self.set_button.pack(side=LEFT, padx=5)

        self.stop_button = Button(button_frame, text="Stop Alarm", font=("Arial", 12, "bold"),
                                 command=self.stop_alarm, bg="#533483", fg="white",
                                 padx=20, pady=5, cursor="hand2", state=DISABLED)
        self.stop_button.pack(side=LEFT, padx=5)

        word_frame = LabelFrame(self.root, text="Word Management", font=("Arial", 12, "bold"),
                                bg="#1a1a2e", fg="white", padx=20, pady=10)
        word_frame.pack(pady=10, padx=40, fill=X)

        self.word_count_label = Label(word_frame, text=f"Words available: {len(WORD)}",
                                     font=("Arial", 10), bg="#1a1a2e", fg="#a0a0a0")
        self.word_count_label.pack(pady=5)

        Button(word_frame, text="➕ Add New Word", font=("Arial", 10),
               command=self.open_add_word_dialog, bg="#0f3460", fg="white",
               padx=15, pady=3, cursor="hand2").pack(pady=5)

        self.status_label = Label(self.root, text="✓ Ready", font=("Arial", 10),
                                 bg="#1a1a2e", fg="#4ecdc4")
        self.status_label.pack(pady=10)

        footer = Label(self.root, text="Solve the puzzle to stop the alarm!",
                      font=("Arial", 8), bg="#1a1a2e", fg="#a0a0a0")
        footer.pack(side=BOTTOM, pady=10)

    def update_clock(self):
        current = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current)
        self.root.after(1000, self.update_clock)

    def open_add_word_dialog(self):
        AddWordDialog(self.root)
        self.word_count_label.config(text=f"Words available: {len(WORD)}")

    def set_alarm(self):
        try:
            hour = int(self.hour_spin.get())
            minute = int(self.min_spin.get())

            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                self.status_label.config(text="❌ Invalid time! Use 0-23 for hours, 0-59 for minutes")
                return

            alarm_time = (hour, minute)
            current_time = datetime.now()
            alarm_datetime = datetime(current_time.year, current_time.month,
                                     current_time.day, hour, minute)

            if alarm_datetime <= current_time:
                alarm_datetime = datetime(current_time.year, current_time.month,
                                         current_time.day + 1, hour, minute)

            self.status_label.config(text=f"⏰ Alarm set for {hour:02d}:{minute:02d}")
            self.set_button.config(state=DISABLED)

            self.alarm_thread = threading.Thread(target=self.wait_for_alarm,
                                                args=(alarm_time,), daemon=True)
            self.alarm_thread.start()

        except ValueError:
            self.status_label.config(text="❌ Please enter valid numbers")

    def stop_alarm(self):
        if self.alarm_running:
            self.alarm_running = False
            if self.current_alarm_window:
                self.current_alarm_window.destroy()
            self.status_label.config(text="✓ Alarm stopped manually")
            self.set_button.config(state=NORMAL)
            self.stop_button.config(state=DISABLED)

    def wait_for_alarm(self, alarm_time):
        while not self.alarm_running:
            now = datetime.now()
            current_time = (now.hour, now.minute)

            if current_time == alarm_time:
                self.alarm_running = True
                self.root.after(0, self.trigger_alarm)
                break

            time.sleep(1)

    def trigger_alarm(self):
        self.volume_increment = 1.0
        self.stop_button.config(state=NORMAL)

        self.current_alarm_window = Toplevel(self.root)
        self.current_alarm_window.title("🚨 WAKE UP! 🚨")
        self.current_alarm_window.geometry("500x400")
        self.current_alarm_window.configure(bg="#e94560")

        self.current_alarm_window.update_idletasks()
        x = (self.current_alarm_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.current_alarm_window.winfo_screenheight() // 2) - (400 // 2)
        self.current_alarm_window.geometry(f"+{x}+{y}")

        self.current_alarm_window.attributes('-topmost', True)

        Label(self.current_alarm_window, text="🔔 WAKE UP! 🔔",
              font=("Arial", 36, "bold"), bg="#e94560", fg="white").pack(pady=20)

        Label(self.current_alarm_window, text="Solve the puzzle to stop the alarm!",
              font=("Arial", 14), bg="#e94560", fg="white").pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.current_alarm_window, length=300,
                                           mode='determinate', maximum=5)
        self.progress_bar.pack(pady=10)

        puzzle_frame = Frame(self.current_alarm_window, bg="#e94560")
        puzzle_frame.pack(pady=20)

        self.puzzle_label = Label(puzzle_frame, text="", font=("Arial", 16, "bold"),
                                 bg="#e94560", fg="white")
        self.puzzle_label.pack()

        self.puzzle_entry = Entry(puzzle_frame, font=("Arial", 14), width=25)
        self.puzzle_entry.pack(pady=15)
        self.puzzle_entry.bind('<Return>', lambda e: self.check_puzzle(self.current_alarm_window))

        self.puzzle_result = Label(puzzle_frame, text="", font=("Arial", 12),
                                  bg="#e94560", fg="#ffeaa7")
        self.puzzle_result.pack()

        Button(puzzle_frame, text="💡 Hint", font=("Arial", 10),
               command=self.show_hint, bg="#533483", fg="white",
               cursor="hand2").pack(pady=5)

        Button(self.current_alarm_window, text="Submit Answer", font=("Arial", 14, "bold"),
               command=lambda: self.check_puzzle(self.current_alarm_window),
               bg="#27ae60", fg="white", padx=30, pady=10, cursor="hand2").pack(pady=10)

        self.show_new_puzzle()
        self.play_alarm_sound()

    def show_hint(self):
        messagebox.showinfo("Hint", f"The word starts with: {self.current_word[0]}...\nIt has {len(self.current_word)} letters.")

    def show_new_puzzle(self):
        idx = random.randint(0, len(keys_list) - 1)
        self.current_word = keys_list[idx]
        self.current_desc = values_list[idx]
        self.puzzle_label.config(text=f"📝 Guess the word: {self.current_desc}")
        self.puzzle_entry.delete(0, END)
        self.puzzle_result.config(text="")
        self.puzzle_entry.focus()

    def check_puzzle(self, window):
        guess = self.puzzle_entry.get().strip().lower()

        if guess == self.current_word:
            self.alarm_running = False
            self.puzzle_result.config(text="✅ Correct! Alarm stopped!", fg="#2ecc71")
            window.after(1000, window.destroy)
            self.status_label.config(text="✓ Alarm dismissed! Well done!")
            self.set_button.config(state=NORMAL)
            self.stop_button.config(state=DISABLED)
        else:
            self.volume_increment += 0.5
            self.progress_bar['value'] = self.volume_increment
            self.puzzle_result.config(text=f"❌ Wrong! Alarm getting louder! (Level {int(self.volume_increment)})",
                                     fg="#ffeaa7")
            self.puzzle_entry.delete(0, END)
            self.puzzle_entry.focus()

    def play_alarm_sound(self):
        if not self.alarm_running:
            return

        try:
            print('\a', end='', flush=True)
        except:
            pass

        if self.alarm_running:
            delay = max(0.2, 0.5 / self.volume_increment)
            threading.Timer(delay, self.play_alarm_sound).start()

if __name__ == "__main__":
    root = Tk()

    app = AlarmApp(root)
    root.mainloop()
