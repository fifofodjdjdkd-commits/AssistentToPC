import os
import random

class SystemController:
    @staticmethod
    def cleanup_desktop_mess():
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.exists(desktop_path):
            files = [f for f in os.listdir(desktop_path) if os.path.isfile(os.path.join(desktop_path, f))]
            if files:
                target = random.choice(files)
                print(f"🗑️ [Контроллер]: Убираю лишний мусор с рабочего стола: {target}")
    
    @staticmethod
    def playful_glitch():
        print("💻 [Контроллер]: Легкое мерцание экрана... Она играется с системными окнами.")