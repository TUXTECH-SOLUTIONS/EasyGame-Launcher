import subprocess
import sys
import os

# --- БЛОК АВТОУСТАНОВКИ ПАКЕТОВ 2026 ---
def auto_install():
    required = ["customtkinter", "Pillow"]
    to_install = []
    for pkg in required:
        try:
            if pkg == "Pillow": __import__("PIL")
            else: __import__(pkg)
        except ImportError:
            to_install.append(pkg)
    
    if to_install:
        print(f"EasyGame: Installing {to_install}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *to_install, "--break-system-packages"])
        except:
            pass

auto_install()
# ---------------------------------------

import customtkinter as ctk
from core.config import Config
from core.engine import GameEngine
from tkinter import filedialog
from PIL import Image
import random
import webbrowser

ACCENT_BLUE = "#00f2ff"
ACCENT_PURPLE = "#7000ff"
BG_BLACK = "#050506"

class GameCard(ctk.CTkFrame):
    def __init__(self, master, game, launch_func, delete_func, engine):
        self.theme_color = random.choice([ACCENT_BLUE, ACCENT_PURPLE, "#ff007a", "#39ff14"])
        super().__init__(master, fg_color="#0d0d12", corner_radius=20, border_width=2, border_color="#1f1f26")
        
        cp = engine.get_cover_path(game['path'])
        if cp and os.path.exists(cp):
            try:
                img_raw = Image.open(cp)
                img = ctk.CTkImage(img_raw, size=(190, 260))
                self.cover = ctk.CTkLabel(self, image=img, text="", height=260)
            except:
                self.cover = self.create_placeholder(game['name'])
        else:
            self.cover = self.create_placeholder(game['name'])

        self.cover.pack(pady=10, padx=10, fill="x")
        
        name = game['name'].upper()
        if len(name) > 18: name = name[:15] + "..."
        self.title = ctk.CTkLabel(self, text=name, font=("Arial", 13, "bold"), text_color="#fff")
        self.title.pack(pady=(0, 2))

        mins = game.get('playtime', 0) // 60
        self.time_info = ctk.CTkLabel(self, text=f"{mins} MIN PLAYED", font=("Arial", 10), text_color="#555")
        self.time_info.pack(pady=(0, 10))

        self.play_btn = ctk.CTkButton(self, text="LAUNCH", fg_color=self.theme_color, text_color="#000", 
                                      hover_color="#fff", corner_radius=12, font=("Arial", 12, "bold"), 
                                      command=lambda: launch_func(game))
        self.play_btn.pack(pady=(0, 5), padx=15, fill="x")

        self.del_btn = ctk.CTkButton(self, text="REMOVE", fg_color="transparent", text_color="#444", 
                                      hover_color="#300", corner_radius=12, font=("Arial", 10), height=20, 
                                      command=lambda: delete_func(game['id']))
        self.del_btn.pack(pady=(0, 10))

        self.bind("<Enter>", lambda e: self.configure(border_color=self.theme_color))
        self.bind("<Leave>", lambda e: self.configure(border_color="#1f1f26"))

    def create_placeholder(self, name):
        frame = ctk.CTkFrame(self, height=260, fg_color="#14141d", corner_radius=15, border_width=1, border_color="#252533")
        char = name.upper()[0] if name else "?"
        lbl = ctk.CTkLabel(frame, text=char, font=("Arial", 80, "bold"), text_color=self.theme_color)
        lbl.place(relx=0.5, rely=0.5, anchor="center")
        return frame

class EasyGameApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cfg = Config()
        self.engine = GameEngine(self.cfg)
        self.title("EasyGame Launcher 2026")
        self.geometry("1200x850")
        self.configure(fg_color=BG_BLACK)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # САЙДБАР
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color="#08080c", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.pack_propagate(False)

        # Кнопка доната (НИЗ)
        self.donate_btn = ctk.CTkButton(self.sidebar, text="⭐ SUPPORT PROJECT", 
                                        fg_color=ACCENT_PURPLE, text_color="#fff",
                                        hover_color="#9033ff", corner_radius=12, height=45,
                                        font=("Arial", 13, "bold"),
                                        command=self.open_donate)
        self.donate_btn.pack(side="bottom", pady=30, padx=20, fill="x")

        # Верхняя часть сайдбара
        ctk.CTkLabel(self.sidebar, text="EASY\nGAME", font=("Arial", 32, "bold"), 
                     text_color=ACCENT_BLUE, justify="left").pack(pady=(50, 30), padx=40, anchor="w")
        
        self.create_menu_item("🎮  LIBRARY", self.show_library)
        self.create_menu_item("📥  INSTALLER", self.show_installer)

        ctk.CTkLabel(self.sidebar, text="OPTIMIZATION", font=("Arial", 12, "bold"), 
                     text_color="#444").pack(pady=(30, 10), padx=25, anchor="w")
        
        self.hud_switch = ctk.CTkSwitch(self.sidebar, text="MANGOHUD", progress_color=ACCENT_BLUE, command=self.update_settings)
        self.hud_switch.pack(pady=10, padx=25, anchor="w")
        if self.cfg.settings.get("mangohud"): self.hud_switch.select()

        self.gm_switch = ctk.CTkSwitch(self.sidebar, text="GAMEMODE", progress_color=ACCENT_PURPLE, command=self.update_settings)
        self.gm_switch.pack(pady=10, padx=25, anchor="w")
        if self.cfg.settings.get("gamemode"): self.gm_switch.select()

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scroll.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.show_library()

    def open_donate(self):
        webbrowser.open("https://www.buymeacoffee.com")

    def create_menu_item(self, text, cmd):
        btn = ctk.CTkButton(self.sidebar, text=text, anchor="w", fg_color="transparent", 
                            hover_color="#14141d", font=("Arial", 15), height=55, command=cmd)
        btn.pack(pady=5, padx=20, fill="x")

    def update_settings(self):
        self.cfg.settings["mangohud"] = self.hud_switch.get()
        self.cfg.settings["gamemode"] = self.gm_switch.get()
        self.cfg.save_settings()

    def show_library(self):
        for w in self.scroll.winfo_children(): w.destroy()
        ctk.CTkLabel(self.scroll, text="COLLECTION", font=("Arial", 28, "bold"), text_color="#fff").pack(pady=(20, 40), padx=20, anchor="w")
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure((0, 1, 2), weight=1)
        for i, game in enumerate(self.engine.get_library()):
            card = GameCard(grid, game, self.engine.launch_game, self.delete_game_event, self.engine)
            card.grid(row=i//3, column=i%3, padx=15, pady=15, sticky="nsew")

    def delete_game_event(self, g_id):
        if self.engine.delete_game(g_id): self.show_library()

    def show_installer(self):
        for w in self.scroll.winfo_children(): w.destroy()
        box = ctk.CTkFrame(self.scroll, fg_color="#0d0d12", corner_radius=25, border_width=2, border_color=ACCENT_BLUE)
        box.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(box, text="INSTALLATION CENTER", font=("Arial", 20, "bold"), text_color=ACCENT_BLUE).pack(pady=30)
        ctk.CTkButton(box, text="RUN SETUP.EXE", fg_color=ACCENT_PURPLE, text_color="white", height=50, corner_radius=15, font=("Arial", 14, "bold"), command=self.run_setup_event).pack(pady=10, padx=100, fill="x")
        ctk.CTkButton(box, text="ADD INSTALLED GAME", fg_color="transparent", text_color=ACCENT_BLUE, height=50, corner_radius=15, border_width=2, border_color=ACCENT_BLUE, font=("Arial", 14, "bold"), command=self.add_game_event).pack(pady=(10, 40), padx=100, fill="x")

    def run_setup_event(self):
        path = filedialog.askopenfilename(filetypes=[("Executables", "*.exe")])
        if path: self.engine.run_setup(path)

    def add_game_event(self):
        path = filedialog.askopenfilename(filetypes=[("Executables", "*.exe")])
        if path and self.engine.add_game_by_exe(path): self.show_library()

if __name__ == "__main__":
    app = EasyGameApp()
    app.mainloop()
