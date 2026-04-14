import customtkinter as ctk
import tkinter as tk
import pyautogui
import keyboard
import mouse
import threading
import webbrowser
import time
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception as e:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Disable the default PyAutoGUI pause to allow faster clicking
pyautogui.PAUSE = 0

# Set modern theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ModernAutoClicker(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("Nexus Clicker - Modern Edition")
        self.iconbitmap(resource_path("icon.ico"))

        # Window dimensions
        window_width = 450
        window_height = 620

        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate starting X and Y coordinates for Center position
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))

        # Set geometry with center coordinates
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.resizable(False, False)

        # --- State Variables ---
        self.is_clicking = False
        self.click_thread = None
        self.hotkey = 'F6'

        # --- State Variables ---
        self.is_clicking = False
        self.click_thread = None
        self.hotkey = 'F6'

        # เพิ่มตัวแปรสำหรับระบบ Macro
        self.recorded_events = []
        self.is_recording = False
        self.is_playing_macro = False

        # Build UI Elements
        self.setup_ui()

        # Register the hotkeys
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
        keyboard.add_hotkey('ctrl+3', self.toggle_recording)  # ปุ่ม Record ตามหน้า Setting รูปที่ 4
        keyboard.add_hotkey('ctrl+1', self.toggle_playback)  # ปุ่ม Play ตามหน้า Setting รูปที่ 4

        # Build UI Elements
        self.setup_ui()

        # Register the hotkey
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)

    def setup_ui(self):
        # Main Title
        self.title_label = ctk.CTkLabel(self, text="NEXUS CLICKER", font=("Arial Black", 24), text_color="#3a7ebf")
        self.title_label.pack(pady=(20, 10))

        # --- 1. Interval Settings (Card Style) ---
        self.interval_card = ctk.CTkFrame(self, corner_radius=15)
        self.interval_card.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.interval_card, text="⏱️ Click Interval", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                                    pady=(10, 5))

        interval_grid = ctk.CTkFrame(self.interval_card, fg_color="transparent")
        interval_grid.pack(fill="x", padx=15, pady=(0, 15))

        # Entries setup inside the grid
        self.entry_hours = self._create_time_input(interval_grid, "Hours", 0, 0)
        self.entry_mins = self._create_time_input(interval_grid, "Mins", 0, 1)
        self.entry_secs = self._create_time_input(interval_grid, "Secs", 0, 2)
        self.entry_ms = self._create_time_input(interval_grid, "MS", 0, 3, default_val="100")

        # --- 2. Options & Repeat Settings (Two Columns) ---
        self.middle_container = ctk.CTkFrame(self, fg_color="transparent")
        self.middle_container.pack(pady=5, padx=20, fill="x")
        self.middle_container.grid_columnconfigure(0, weight=1)
        self.middle_container.grid_columnconfigure(1, weight=1)

        # Left Column: Mouse Options
        self.options_card = ctk.CTkFrame(self.middle_container, corner_radius=15)
        self.options_card.grid(row=0, column=0, padx=(0, 5), sticky="nsew")

        ctk.CTkLabel(self.options_card, text="🖱️ Mouse", font=("Arial", 14, "bold")).pack(anchor="w", padx=10,
                                                                                          pady=(10, 5))
        self.btn_var = ctk.StringVar(value="Left")
        self.combo_btn = ctk.CTkComboBox(self.options_card, values=["Left", "Right", "Middle"], variable=self.btn_var)
        self.combo_btn.pack(padx=10, pady=5, fill="x")

        self.type_var = ctk.StringVar(value="Single")
        self.combo_type = ctk.CTkComboBox(self.options_card, values=["Single", "Double"], variable=self.type_var)
        self.combo_type.pack(padx=10, pady=(5, 15), fill="x")

        # Right Column: Repeat Options
        self.repeat_card = ctk.CTkFrame(self.middle_container, corner_radius=15)
        self.repeat_card.grid(row=0, column=1, padx=(5, 0), sticky="nsew")

        ctk.CTkLabel(self.repeat_card, text="🔁 Repeat", font=("Arial", 14, "bold")).pack(anchor="w", padx=10,
                                                                                         pady=(10, 5))
        self.repeat_mode = ctk.IntVar(value=2)  # 2 = Until stopped

        ctk.CTkRadioButton(self.repeat_card, text="Until stopped", variable=self.repeat_mode, value=2).pack(anchor="w",
                                                                                                            padx=10,
                                                                                                            pady=5)

        rep_times_frame = ctk.CTkFrame(self.repeat_card, fg_color="transparent")
        rep_times_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkRadioButton(rep_times_frame, text="Times:", variable=self.repeat_mode, value=1).pack(side="left")
        self.entry_repeat_times = ctk.CTkEntry(rep_times_frame, width=50, height=25)
        self.entry_repeat_times.insert(0, "1")
        self.entry_repeat_times.pack(side="right", padx=5)

        # --- 3. Target Position ---
        self.position_card = ctk.CTkFrame(self, corner_radius=15)
        self.position_card.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.position_card, text="🎯 Target Position", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                                    pady=(10, 5))
        self.pos_mode = ctk.IntVar(value=1)  # 1 = Current

        ctk.CTkRadioButton(self.position_card, text="Current mouse location", variable=self.pos_mode, value=1).pack(
            anchor="w", padx=15, pady=5)

        custom_pos_frame = ctk.CTkFrame(self.position_card, fg_color="transparent")
        custom_pos_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkRadioButton(custom_pos_frame, text="", variable=self.pos_mode, value=2, width=20).pack(side="left")
        self.btn_pick_loc = ctk.CTkButton(custom_pos_frame, text="Pick Location", width=100, command=self.pick_location)
        self.btn_pick_loc.pack(side="left", padx=5)

        ctk.CTkLabel(custom_pos_frame, text="X:").pack(side="left", padx=5)
        self.entry_x = ctk.CTkEntry(custom_pos_frame, width=50, height=28)
        self.entry_x.insert(0, "0")
        self.entry_x.pack(side="left")

        ctk.CTkLabel(custom_pos_frame, text="Y:").pack(side="left", padx=5)
        self.entry_y = ctk.CTkEntry(custom_pos_frame, width=50, height=28)
        self.entry_y.insert(0, "0")
        self.entry_y.pack(side="left")

        # --- 4. Main Action Buttons ---
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=10, padx=20, fill="x")
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)

        self.btn_start = ctk.CTkButton(self.action_frame, text=f"START ({self.hotkey})",
                                       font=("Arial Black", 18),
                                       text_color="#ffffff",
                                       fg_color="#2ecc71",
                                       hover_color="#27ae60",
                                       border_width=4,
                                       border_color="#1e8449",
                                       height=45,
                                       command=self.start_from_button)
        self.btn_start.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # ปุ่ม STOP (เพิ่มเส้นขอบสีแดงเข้ม)
        self.btn_stop = ctk.CTkButton(self.action_frame, text=f"STOP ({self.hotkey})",
                                      font=("Arial Black", 18),
                                      fg_color="#e74c3c",
                                      hover_color="#c0392b",
                                      border_width=4,
                                      border_color="#922b21",
                                      height=45,
                                      state="disabled",
                                      command=self.stop_from_button)
        self.btn_stop.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # --- 5. Extra Tools (Hotkey & Record) ---
        self.tools_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tools_frame.pack(pady=(0, 10), padx=20, fill="x")
        self.tools_frame.grid_columnconfigure(0, weight=1)
        self.tools_frame.grid_columnconfigure(1, weight=1)

        # Hotkey Setting Button
        self.btn_hotkey = ctk.CTkButton(self.tools_frame, text="Hotkey Setting", font=("Arial", 14, "bold"),
                                        fg_color="#34495e", hover_color="#2c3e50", height=35,
                                        command=self.open_hotkey_settings)
        self.btn_hotkey.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # Record & Playback Button (Activated for Phase 2)
        self.btn_record = ctk.CTkButton(self.tools_frame, text="Record & Playback", font=("Arial", 14, "bold"),
                                        fg_color="#34495e", hover_color="#2c3e50", height=35,
                                        command=self.open_record_playback)
        self.btn_record.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    # Helper function to create clean inputs
    def _create_time_input(self, parent, label, row, col, default_val="0"):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, padx=5, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        entry = ctk.CTkEntry(frame, justify="center")
        entry.insert(0, default_val)
        entry.pack(fill="x", pady=2)
        ctk.CTkLabel(frame, text=label, font=("Arial", 10)).pack()
        return entry

    # --- Core Logic Functions (Kept identical to ensure stability) ---
    def pick_location(self):
        self.btn_pick_loc.configure(text="Wait 3s...", fg_color="#e67e22", hover_color="#d35400")
        self.update()
        time.sleep(3)

        x, y = pyautogui.position()

        self.entry_x.delete(0, 'end')
        self.entry_x.insert(0, str(x))
        self.entry_y.delete(0, 'end')
        self.entry_y.insert(0, str(y))
        self.pos_mode.set(2)

        self.btn_pick_loc.configure(text="Pick Location", fg_color=["#3a7ebf", "#1f538d"],
                                    hover_color=["#325882", "#14375e"])

    def get_exact_delay(self):
        try:
            h = float(self.entry_hours.get() or 0)
            m = float(self.entry_mins.get() or 0)
            s = float(self.entry_secs.get() or 0)
            ms = float(self.entry_ms.get() or 0)
            total_seconds = (h * 3600) + (m * 60) + s + (ms / 1000.0)
            return max(total_seconds, 0.001)
        except ValueError:
            return 0.1

    def start_from_button(self):
        if not self.is_clicking:
            self.toggle_clicking()

    def stop_from_button(self):
        if self.is_clicking:
            self.toggle_clicking()

    def toggle_clicking(self):
        self.is_clicking = not self.is_clicking

        if self.is_clicking:
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.title_label.configure(text="● RUNNING", text_color="#2ecc71")

            self.click_thread = threading.Thread(target=self.clicker_loop)
            self.click_thread.daemon = True
            self.click_thread.start()
        else:
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.title_label.configure(text="NEXUS CLICKER", text_color="#3a7ebf")

    def clicker_loop(self):
        delay = self.get_exact_delay()
        mouse_btn = self.btn_var.get().lower()
        clicks_count = 2 if self.type_var.get() == "Double" else 1

        use_specific_pos = (self.pos_mode.get() == 2)
        target_x, target_y = None, None

        if use_specific_pos:
            try:
                target_x = int(self.entry_x.get())
                target_y = int(self.entry_y.get())
            except ValueError:
                use_specific_pos = False

        repeat_mode = self.repeat_mode.get()
        max_repeats = 0
        if repeat_mode == 1:
            try:
                max_repeats = int(self.entry_repeat_times.get())
            except ValueError:
                max_repeats = 1

        current_repeat = 0

        while self.is_clicking:
            if repeat_mode == 1 and current_repeat >= max_repeats:
                self.stop_from_button()
                break

            if use_specific_pos:
                pyautogui.click(x=target_x, y=target_y, button=mouse_btn, clicks=clicks_count)
            else:
                pyautogui.click(button=mouse_btn, clicks=clicks_count)

            current_repeat += 1
            time.sleep(delay)

    # ==========================================
    # --- Phase 1: Hotkey Setting Logic (Updated 2.0) ---
    # ==========================================
    def open_hotkey_settings(self):
        # สร้างหน้าต่าง Popup
        self.hotkey_window = ctk.CTkToplevel(self)
        self.hotkey_window.title("Hotkey Setting")

        # คำนวณให้ Popup อยู่กึ่งกลางของหน้าต่างหลัก (Main Window)
        popup_width = 320
        popup_height = 150

        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_w = self.winfo_width()
        main_h = self.winfo_height()

        center_x = main_x + (main_w // 2) - (popup_width // 2)
        center_y = main_y + (main_h // 2) - (popup_height // 2)

        self.hotkey_window.geometry(f"{popup_width}x{popup_height}+{center_x}+{center_y}")
        self.hotkey_window.resizable(False, False)
        self.hotkey_window.grab_set()

        self.temp_hotkey = self.hotkey

        # --- สร้าง UI ให้เหมือนต้นฉบับเป๊ะๆ ---
        top_frame = ctk.CTkFrame(self.hotkey_window, fg_color="transparent")
        top_frame.pack(pady=(25, 15), padx=20, fill="x")
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)

        # ปุ่มซ้าย: Start / Stop (เปลี่ยนเป็นปุ่มกดแล้ว!)
        self.btn_action = ctk.CTkButton(top_frame, text="Start / Stop", fg_color="#3a7ebf", hover_color="#2c3e50",
                                        width=110, command=self.listen_for_key)
        self.btn_action.grid(row=0, column=0, padx=(0, 5))

        # ช่องขวา: แสดง Hotkey ปัจจุบัน (โชว์เฉยๆ กดไม่ได้)
        self.lbl_current_key = ctk.CTkButton(top_frame, text=self.temp_hotkey, font=("Arial", 16, "bold"),
                                             fg_color="#7f8c8d", text_color_disabled="white", state="disabled",
                                             width=110)
        self.lbl_current_key.grid(row=0, column=1, padx=(5, 0))

        # กรอบด้านล่าง (ปุ่ม Ok / Cancel)
        bot_frame = ctk.CTkFrame(self.hotkey_window, fg_color="transparent")
        bot_frame.pack(pady=10)

        btn_ok = ctk.CTkButton(bot_frame, text="Ok", width=90, fg_color="#2ecc71", hover_color="#27ae60",
                               command=self.save_hotkey)
        btn_ok.pack(side="left", padx=10)

        btn_cancel = ctk.CTkButton(bot_frame, text="Cancel", width=90, fg_color="#e74c3c", hover_color="#c0392b",
                                   command=self.hotkey_window.destroy)
        btn_cancel.pack(side="left", padx=10)

    def listen_for_key(self):
        # ปิดการทำงานปุ่ม Start/Stop ชั่วคราว กันกดเบิ้ล
        self.btn_action.configure(state="disabled")
        # เปลี่ยนสีช่องแสดงผลด้านขวาให้เป็นสีส้ม เพื่อบอกว่ากำลังรอรับปุ่ม
        self.lbl_current_key.configure(text="Press Key...", fg_color="#e67e22")
        threading.Thread(target=self._wait_key_thread, daemon=True).start()

    def _wait_key_thread(self):
        time.sleep(0.2)

        event = keyboard.read_event()
        while event.event_type != keyboard.KEY_DOWN:
            event = keyboard.read_event()

        self.temp_hotkey = event.name.upper()

        # อัปเดตหน้า UI กลับมาเป็นปกติอย่างปลอดภัย
        self.after(0, self._update_ui_after_key)

    def _update_ui_after_key(self):
        # คืนค่า UI กลับเป็นปกติ
        self.lbl_current_key.configure(text=self.temp_hotkey, fg_color="#7f8c8d")
        self.btn_action.configure(state="normal")

    def save_hotkey(self):
        try:
            keyboard.remove_hotkey(self.hotkey)
        except Exception:
            pass

        self.hotkey = self.temp_hotkey
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)

        self.btn_start.configure(text=f"START ({self.hotkey})")
        self.btn_stop.configure(text=f"STOP ({self.hotkey})")

        self.hotkey_window.destroy()

    # ==========================================
    # --- Phase 2: Record & Playback UI System ---
    # ==========================================
    def _center_any_window(self, target_window, w, h):
        # Helper function to center any window on the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (w / 2))
        y = int((screen_height / 2) - (h / 2))
        target_window.geometry(f"{w}x{h}+{x}+{y}")

    def open_record_playback(self):
        # 1. Hide the main window
        self.withdraw()

        # 2. Create the small Record/Playback toolbar window
        self.rp_window = ctk.CTkToplevel(self)
        self.rp_window.title("OP A...")
        self._center_any_window(self.rp_window, 280, 100)
        self.rp_window.resizable(False, False)

        # Override the 'X' close button to show main window instead of exiting
        self.rp_window.protocol("WM_DELETE_WINDOW", self.close_record_playback)

        # 3. Create standard Windows Menu Bar (Ribbon)
        menubar = tk.Menu(self.rp_window)

        # Main 'Options' Menu
        options_menu = tk.Menu(menubar, tearoff=0)

        # Submenu: Playback
        playback_menu = tk.Menu(options_menu, tearoff=0)
        playback_menu.add_command(label="Speed", command=self.open_playback_speed)
        playback_menu.add_command(label="Repeat", command=self.open_playback_repeat)

        # Submenu: Recording
        recording_menu = tk.Menu(options_menu, tearoff=0)
        recording_menu.add_command(label="Options", command=self.open_recording_options)

        # Submenu: Settings
        settings_menu = tk.Menu(options_menu, tearoff=0)
        settings_menu.add_command(label="Hotkeys", command=self.open_hotkeys_setting)
        settings_menu.add_command(label="View", command=self.open_view_setting)
        settings_menu.add_command(label="Other", command=self.open_other_setting)

        # Attach submenus to main Options menu
        options_menu.add_cascade(label="Playback", menu=playback_menu)
        options_menu.add_cascade(label="Recording", menu=recording_menu)
        options_menu.add_cascade(label="Settings", menu=settings_menu)

        menubar.add_cascade(label="Options", menu=options_menu)
        self.rp_window.config(menu=menubar)  # Apply menu to window

        # 4. Create UI Buttons (Play, Record, More)
        btn_frame = ctk.CTkFrame(self.rp_window, fg_color="transparent")
        btn_frame.pack(pady=15, expand=True)

        self.btn_play = ctk.CTkButton(btn_frame, text="▶", font=("Arial", 24), text_color="#7BB53B", fg_color="white",
                                      hover_color="#f1f2f6", width=50, height=40, corner_radius=5,
                                      command=self.toggle_playback)
        self.btn_play.pack(side="left", padx=5)

        self.btn_rec = ctk.CTkButton(btn_frame, text="●", font=("Arial", 20), text_color="#e74c3c", fg_color="white",
                                     hover_color="#f1f2f6", width=50, height=40, corner_radius=5,
                                     command=self.toggle_recording)
        self.btn_rec.pack(side="left", padx=5)

        btn_more = ctk.CTkButton(btn_frame, text="More", text_color="black", fg_color="white", hover_color="#f1f2f6",
                                 width=60, height=40, corner_radius=5,
                                 command=self.open_rickroll)
        btn_more.pack(side="left", padx=5)

    def close_record_playback(self):
        # Destroy the small window
        self.rp_window.destroy()
        # Show main window again
        self.deiconify()
        # Recenter main window
        self._center_any_window(self, 450, 680)

    def open_rickroll(self):
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    # --- Popups for Recording > Options ---
    def open_recording_options(self):
        rec_opt_win = ctk.CTkToplevel(self.rp_window)
        rec_opt_win.title("Recording options")
        self._center_any_window(rec_opt_win, 280, 160)
        rec_opt_win.resizable(False, False)
        rec_opt_win.grab_set()

        frame = ctk.CTkFrame(rec_opt_win, fg_color="transparent")
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkCheckBox(frame, text="Mouse click").grid(row=0, column=0, pady=10, sticky="w")
        ctk.CTkCheckBox(frame, text="Mouse move").grid(row=0, column=1, pady=10, padx=20, sticky="w")
        ctk.CTkCheckBox(frame, text="Delay").grid(row=1, column=0, pady=5, sticky="w")

        bot_frame = ctk.CTkFrame(rec_opt_win, fg_color="transparent")
        bot_frame.pack(pady=10)
        ctk.CTkButton(bot_frame, text="Ok", width=80, fg_color="white", text_color="black",
                      command=rec_opt_win.destroy).pack(side="left", padx=10)
        ctk.CTkButton(bot_frame, text="Cancel", width=80, fg_color="white", text_color="black",
                      command=rec_opt_win.destroy).pack(side="left", padx=10)

    # --- Popups for Settings > Hotkeys ---
    def open_hotkeys_setting(self):
        hk_win = ctk.CTkToplevel(self.rp_window)
        hk_win.title("Hotkeys Setting")
        self._center_any_window(hk_win, 300, 180)
        hk_win.resizable(False, False)
        hk_win.grab_set()

        frame = ctk.CTkFrame(hk_win, fg_color="transparent")
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkButton(frame, text="Playback/Stop", fg_color="white", text_color="black", width=120).grid(row=0,
                                                                                                         column=0,
                                                                                                         pady=5, padx=5)
        ctk.CTkLabel(frame, text="CTRL+1", font=("Arial", 16, "bold"), bg_color="white", width=100).grid(row=0,
                                                                                                         column=1,
                                                                                                         pady=5, padx=5)

        ctk.CTkButton(frame, text="Record/Stop", fg_color="white", text_color="black", width=120).grid(row=1, column=0,
                                                                                                       pady=5, padx=5)
        ctk.CTkLabel(frame, text="CTRL+3", font=("Arial", 16, "bold"), bg_color="white", width=100).grid(row=1,
                                                                                                         column=1,
                                                                                                         pady=5, padx=5)

        bot_frame = ctk.CTkFrame(hk_win, fg_color="transparent")
        bot_frame.pack(pady=10)
        ctk.CTkButton(bot_frame, text="Ok", width=80, fg_color="white", text_color="black",
                      command=hk_win.destroy).pack(side="left", padx=10)
        ctk.CTkButton(bot_frame, text="Cancel", width=80, fg_color="white", text_color="black",
                      command=hk_win.destroy).pack(side="left", padx=10)

    # --- Popups for Settings > View ---
    def open_view_setting(self):
        view_win = ctk.CTkToplevel(self.rp_window)
        view_win.title("View Setting")
        self._center_any_window(view_win, 280, 160)
        view_win.resizable(False, False)
        view_win.grab_set()

        frame = ctk.CTkFrame(view_win, fg_color="transparent")
        frame.pack(pady=20, padx=30, fill="both", expand=True)

        ctk.CTkCheckBox(frame, text="Minimized when playing").pack(anchor="w", pady=5)
        ctk.CTkCheckBox(frame, text="Minimized when recording").pack(anchor="w", pady=(10, 5))

        bot_frame = ctk.CTkFrame(view_win, fg_color="transparent")
        bot_frame.pack(pady=10)
        ctk.CTkButton(bot_frame, text="Ok", width=80, fg_color="white", text_color="black",
                      command=view_win.destroy).pack(side="left", padx=10)
        ctk.CTkButton(bot_frame, text="Cancel", width=80, fg_color="white", text_color="black",
                      command=view_win.destroy).pack(side="left", padx=10)

    # --- Popups for Settings > Other ---
    def open_other_setting(self):
        other_win = ctk.CTkToplevel(self.rp_window)
        other_win.title("Other setting")
        self._center_any_window(other_win, 300, 200)
        other_win.resizable(False, False)
        other_win.grab_set()

        # Create a visually grouped frame
        group_frame = ctk.CTkFrame(other_win, corner_radius=5)
        group_frame.pack(pady=15, padx=20, fill="x")

        ctk.CTkLabel(group_frame, text="On playback complete", font=("Arial", 12)).pack(anchor="w", padx=10,
                                                                                        pady=(5, 0))

        combo_options = [
            "Idle", "Quit", "Lock computer", "Log off computer",
            "Turn off computer", "Standby", "Hibernate (only if supported)"
        ]
        ctk.CTkComboBox(group_frame, values=combo_options, width=240, fg_color="white", text_color="black").pack(
            pady=(5, 15), padx=10)

        ctk.CTkCheckBox(other_win, text="Display balloon tip").pack(anchor="w", padx=20)

        bot_frame = ctk.CTkFrame(other_win, fg_color="transparent")
        bot_frame.pack(pady=15)
        ctk.CTkButton(bot_frame, text="Ok", width=80, fg_color="white", text_color="black",
                      command=other_win.destroy).pack(side="left", padx=10)
        ctk.CTkButton(bot_frame, text="Cancel", width=80, fg_color="white", text_color="black",
                      command=other_win.destroy).pack(side="left", padx=10)

    # --- Popups for Playback > Speed ---
    def open_playback_speed(self):
        speed_win = ctk.CTkToplevel(self.rp_window)
        speed_win.title("Speed setting")
        self._center_any_window(speed_win, 300, 150)
        speed_win.resizable(False, False)
        speed_win.grab_set()

        # ฟังก์ชันอัปเดตตัวหนังสือเวลารูด Slider
        def update_speed_label(value):
            lbl_speed.configure(text=f"Speed: {int(value)} X")

        # ป้ายแสดงความเร็ว
        lbl_speed = ctk.CTkLabel(speed_win, text="Speed: 1 X", font=("Arial", 14))
        lbl_speed.pack(pady=(15, 5))

        # หลอดรูด Slider (ปรับได้ 1-10)
        slider = ctk.CTkSlider(speed_win, from_=1, to=10, number_of_steps=9, command=update_speed_label)
        slider.set(1)  # ค่าเริ่มต้น
        slider.pack(pady=10, padx=20)

        # กรอบปุ่มด้านล่าง
        bot_frame = ctk.CTkFrame(speed_win, fg_color="transparent")
        bot_frame.pack(pady=10)
        ctk.CTkButton(bot_frame, text="Ok", width=80, fg_color="white", text_color="black",
                      command=speed_win.destroy).pack(side="left", padx=10)
        ctk.CTkButton(bot_frame, text="Cancel", width=80, fg_color="white", text_color="black",
                      command=speed_win.destroy).pack(side="left", padx=10)

    # --- Popups for Playback > Repeat ---
    def open_playback_repeat(self):
        rep_win = ctk.CTkToplevel(self.rp_window)
        rep_win.title("Repeat setting")
        self._center_any_window(rep_win, 350, 240)
        rep_win.resizable(False, False)
        rep_win.grab_set()

        # กรอบสี่เหลี่ยมจัดกลุ่ม (เหมือนในรูปต้นฉบับเป๊ะ)
        group_frame = ctk.CTkFrame(rep_win, fg_color=("gray90", "gray20"), corner_radius=5)
        group_frame.pack(pady=15, padx=15, fill="x")

        radio_var = ctk.IntVar(value=1)

        # แถวแรก: Repeat ... times
        f1 = ctk.CTkFrame(group_frame, fg_color="transparent")
        f1.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkRadioButton(f1, text="Repeat", variable=radio_var, value=1).pack(side="left")

        entry_times = ctk.CTkEntry(f1, width=50, justify="center")
        entry_times.insert(0, "1")
        entry_times.pack(side="left", padx=5)
        ctk.CTkLabel(f1, text="times").pack(side="left")

        # แถวที่สอง: Repeat until stopped
        ctk.CTkRadioButton(group_frame, text="Repeat until stopped", variable=radio_var, value=2).pack(anchor="w",
                                                                                                       padx=10,
                                                                                                       pady=(5, 10))

        # แถวที่สาม: Interval (อยู่นอกกรอบ)
        int_frame = ctk.CTkFrame(rep_win, fg_color="transparent")
        int_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkCheckBox(int_frame, text="Interval:").pack(side="left")

        entry_h = ctk.CTkEntry(int_frame, width=40, justify="center")
        entry_h.insert(0, "0")
        entry_h.pack(side="left", padx=(5, 2))
        ctk.CTkLabel(int_frame, text="hours").pack(side="left")

        entry_m = ctk.CTkEntry(int_frame, width=40, justify="center")
        entry_m.insert(0, "0")
        entry_m.pack(side="left", padx=(10, 2))
        ctk.CTkLabel(int_frame, text="mins").pack(side="left")

        entry_s = ctk.CTkEntry(int_frame, width=40, justify="center")
        entry_s.insert(0, "0")
        entry_s.pack(side="left", padx=(10, 2))
        ctk.CTkLabel(int_frame, text="secs").pack(side="left")

        # กรอบปุ่มด้านล่าง
        bot_frame = ctk.CTkFrame(rep_win, fg_color="transparent")
        bot_frame.pack(pady=15)
        ctk.CTkButton(bot_frame, text="Ok", width=80, fg_color="white", text_color="black",
                      command=rep_win.destroy).pack(side="left", padx=10)
        ctk.CTkButton(bot_frame, text="Cancel", width=80, fg_color="white", text_color="black",
                      command=rep_win.destroy).pack(side="left", padx=10)

    # ==========================================
    # --- Phase 3: Macro Record & Playback Logic ---
    # ==========================================
    def toggle_recording(self):
        # ถ้าเปิดหน้าต่างใหญ่อยู่ ให้ไม่ทำงาน (บังคับให้ต้องอยู่โหมดหน้าต่างเล็กถึงจะอัดได้)
        if self.winfo_viewable(): return

        self.is_recording = not self.is_recording

        if self.is_recording:
            # --- เริ่มอัด ---
            self.recorded_events.clear()
            self.btn_rec.configure(text="■", text_color="black")  # เปลี่ยนไอคอนเป็นสี่เหลี่ยมหยุด
            self.rp_window.title("Recording...")

            # หน่วงเวลา 0.3 วิ ก่อนเริ่มอัด เพื่อไม่ให้อัดจังหวะที่เราเอาเมาส์ไปคลิกปุ่ม "เริ่มอัด" ติดไปด้วย
            threading.Timer(0.3, lambda: mouse.hook(self.recorded_events.append)).start()
        else:
            # --- หยุดอัด ---
            try:
                mouse.unhook(self.recorded_events.append)
            except Exception:
                pass
            self.btn_rec.configure(text="●", text_color="#e74c3c")
            self.rp_window.title("OP A...")

    def toggle_playback(self):
        # ไม่ทำงานถ้าหน้าต่างใหญ่เปิดอยู่ หรือ ยังไม่มีข้อมูลที่อัดไว้
        if self.winfo_viewable() or len(self.recorded_events) == 0: return

        self.is_playing_macro = not self.is_playing_macro

        if self.is_playing_macro:
            self.btn_play.configure(text="■", text_color="black")
            self.rp_window.title("Playing...")
            # รัน Playback ใน Thread แยกเพื่อให้หน้าต่าง UI ไม่ค้างเวลาเมาส์ขยับ
            threading.Thread(target=self._playback_thread, daemon=True).start()
        else:
            self.btn_play.configure(text="▶", text_color="#7BB53B")
            self.rp_window.title("OP A...")

    def _playback_thread(self):
        # คำสั่งพระเอก: เล่นการขยับและคลิกทั้งหมดที่อัดไว้ ตามระยะเวลาจริงเป๊ะๆ!
        mouse.play(self.recorded_events)

        # เมื่อเล่นจบครบตามที่อัดไว้ ให้รีเซ็ตปุ่มและสถานะกลับเป็นปกติ
        self.is_playing_macro = False
        self.after(0, lambda: self.btn_play.configure(text="▶", text_color="#7BB53B"))
        self.after(0, lambda: self.rp_window.title("OP A..."))

if __name__ == "__main__":
    app = ModernAutoClicker()
    app.mainloop()