import os
import subprocess
import json
import threading
import time
import shutil

class GameEngine:
    def __init__(self, config):
        self.config = config
        self.prefixes_root = os.path.join(self.config.data_home, "prefixes")
        os.makedirs(self.prefixes_root, exist_ok=True)

    def get_library(self):
        try:
            with open(self.config.db_path, "r") as f:
                return json.load(f)
        except: return []

    def _save_lib(self, library):
        with open(self.config.db_path, "w") as f:
            json.dump(library, f, indent=4)

    def get_cover_path(self, game_path):
        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
        try:
            files = os.listdir(game_path)
            for file in files:
                if any(x in file.lower() for x in ['cover', 'poster', 'folder', 'capsule']):
                    if file.lower().endswith(valid_extensions): return os.path.join(game_path, file)
            for file in files:
                if file.lower().endswith(valid_extensions): return os.path.join(game_path, file)
        except: pass
        return None

    def add_game_by_exe(self, exe_path):
        game_folder = os.path.dirname(exe_path)
        game_name = os.path.basename(game_folder)
        library = self.get_library()
        if any(g.get('exe') == exe_path for g in library): return False
        new_game = {"id": str(int(time.time())), "name": game_name, "exe": exe_path, "path": game_folder, "playtime": 0}
        library.append(new_game)
        self._save_lib(library)
        return True

    def delete_game(self, game_id):
        library = self.get_library()
        new_library = [g for g in library if g.get('id') != game_id]
        prefix_path = os.path.join(self.prefixes_root, str(game_id))
        if os.path.exists(prefix_path):
            try: shutil.rmtree(prefix_path)
            except: pass
        self._save_lib(new_library)
        return True

    def launch_game(self, game_info):
        def _task():
            exe, game_id = game_info.get('exe'), game_info.get('id')
            prefix_path = os.path.join(self.prefixes_root, game_id)
            os.makedirs(prefix_path, exist_ok=True)
            if exe and os.path.exists(exe):
                env = os.environ.copy()
                env["WINEPREFIX"] = prefix_path
                if self.config.settings.get("esync"): env["WINEESYNC"], env["WINEFSYNC"] = "1", "1"
                cmd = ["wine", exe]
                if self.config.settings.get("mangohud") and shutil.which("mangohud"): cmd = ["mangohud"] + cmd
                if self.config.settings.get("gamemode") and shutil.which("gamemoderun"): cmd = ["gamemoderun"] + cmd
                start_ts = time.time()
                try:
                    p = subprocess.Popen(cmd, cwd=os.path.dirname(exe), env=env)
                    p.wait()
                    duration = int(time.time() - start_ts)
                    if duration > 5: self.update_playtime(game_id, duration)
                except: pass
        threading.Thread(target=_task, daemon=True).start()

    def run_setup(self, setup_exe_path):
        def _task():
            setup_prefix = os.path.join(self.config.data_home, "setup_prefix")
            os.makedirs(setup_prefix, exist_ok=True)
            env = os.environ.copy()
            env["WINEPREFIX"] = setup_prefix
            try: subprocess.Popen(["wine", setup_exe_path], cwd=os.path.dirname(setup_exe_path), env=env).wait()
            except: pass
        threading.Thread(target=_task, daemon=True).start()

    def update_playtime(self, g_id, sec):
        lib = self.get_library()
        for g in lib:
            if g.get('id') == g_id: g['playtime'] = g.get('playtime', 0) + sec
        self._save_lib(lib)
