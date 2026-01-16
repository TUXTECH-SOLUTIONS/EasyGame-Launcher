import os
import json

class Config:
    def __init__(self):
        # Определение окружения (Flatpak или обычная система)
        self.is_flatpak = os.path.exists('/.flatpak-info')
        
        if self.is_flatpak:
            self.data_home = os.path.expanduser("~/.var/app/org.easygame.Launcher/data")
        else:
            self.data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share/easygame_2026"))

        self.db_path = os.path.join(self.data_home, "library.json")
        
        # Создаем необходимые папки
        os.makedirs(self.data_home, exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump([], f)

        self.settings = {"theme": "dark", "accent": "#00f2ff"}
        self.settings = {
        "theme": "dark",
        "accent": "#00f2ff",
        "mangohud": True,      # Включение FPS оверлея
        "gamemode": True,      # Включение оптимизации CPU
        "esync": True          # Ускорение многопоточности
}
