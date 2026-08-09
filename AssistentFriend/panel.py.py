import json
import os
import random
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import urllib.request


# ==========================================
# 0. ЦВЕТНОЙ ЛОГИРОВЩИК ДЛЯ КОМАМНДНОЙ СТРОКИ
# ==========================================
class ConsoleLog:
  RESET = "\033[0m"
  WHITE = "\033[97m"
  YELLOW = "\033[93m"
  RED = "\033[91m"

  @classmethod
  def info(cls, text):
    print(f"{cls.WHITE}[ИНФО] {text}{cls.RESET}")

  @classmethod
  def warn(cls, text):
    print(f"{cls.YELLOW}[ПРЕДУПРЕЖДЕНИЕ] {text}{cls.RESET}")

  @classmethod
  def error(cls, text):
    print(f"{cls.RED}[ОШИБКА] {text}{cls.RESET}")


# ==========================================
# 1. ЧИСТАЯ СТРУКТУРА ПАПОК И КОНФИГ
# ==========================================
CONFIG_FILE = "config.json"


def init_clean_structure():
  if not os.path.exists("models"):
    os.makedirs("models")
    ConsoleLog.info("Создана корневая папка 'models/'")
  if not os.path.exists("voices"):
    os.makedirs("voices")
    ConsoleLog.info("Создана корневая папка 'voices/'")


init_clean_structure()


# ==========================================
# 2. МОЗГ ИИ И РАБОТА С ПАПКАМИ И API
# ==========================================
class AICharacterBrain:

  def __init__(self):
    self.stats = {
        "affection": 50,
        "offense": 10,
        "trust": 50,
    }
    ConsoleLog.info("Мозг ИИ успешно инициализирован.")

  def call_real_api(self, model_name, api_url, api_key, user_text):
    """Запрос к API с детальным логированием ошибок"""
    try:
      if (
          "google" in model_name.lower()
          or "aistudio" in api_url.lower()
          or "generativelanguage" in api_url.lower()
      ):
        url = api_url.strip()
        if "generateContent" not in url:
          if not url.endswith("/"):
            url += "/"
          url += "v1beta/models/gemini-2.5-flash:generateContent?key=" + api_key
        else:
          if "?key=" not in url:
            url += "?key=" + api_key

        payload = {"contents": [{"parts": [{"text": user_text}]}]}
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
          with urllib.request.urlopen(req, timeout=15) as response:
            res_body = response.read().decode("utf-8")
            res_data = json.loads(res_body)

            candidates = res_data.get("candidates", [])
            if candidates:
              content = candidates[0].get("content", {})
              parts = content.get("parts", [])
              if parts:
                ai_text = parts[0].get("text", "")
                if ai_text:
                  return ai_text.strip()

            ConsoleLog.warn(
                f"Ответ от Gemini пришел пустой или странной структуры:"
                f" {res_body}"
            )
        except urllib.error.HTTPError as e:
          error_body = e.read().decode("utf-8")
          ConsoleLog.error(f"HTTP Ошибка от Gemini ({e.code}): {error_body}")
        except urllib.error.URLError as e:
          ConsoleLog.error(f"Ошибка сети/подключения к Google AI Studio: {e.reason}")

      else:
        url = api_url.strip()
        payload = {
            "model": (
                "deepseek-chat" if "deepseek" in model_name.lower() else "gpt-4o"
            ),
            "messages": [{"role": "user", "content": user_text}],
        }
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as response:
          res_data = json.loads(response.read().decode("utf-8"))
          ai_text = (
              res_data.get("choices", [{}])[0]
              .get("message", {})
              .get("content", "")
          )
          if ai_text:
            return ai_text.strip()

    except Exception as e:
      ConsoleLog.error(f"Непредвиденная ошибка при запросе к API: {e}")

    return None

  def evaluate_and_act(
      self, character_name, user_text, model_name, api_url, api_key
  ):
    text_lower = user_text.lower()
    ConsoleLog.info(
        f"ИИ обрабатывает запрос для '{character_name}' через модель"
        f" '{model_name}': '{user_text}'"
    )

    if len(user_text.strip()) < 3:
      self.stats["offense"] += 25
      self.stats["affection"] -= 10
      ConsoleLog.warn(
          "Сообщение слишком короткое. Уровень обиды персонажа вырос!"
      )
    elif "извини" in text_lower or "прости" in text_lower or "люблю" in text_lower:
      self.stats["offense"] = max(0, self.stats["offense"] - 35)
      self.stats["affection"] += 20
      ConsoleLog.info("Игрок извинился. Уровень обиды снижен.")
    else:
      self.stats["offense"] = max(0, self.stats["offense"] - 5)

    self.stats["offense"] = max(0, min(100, self.stats["offense"]))
    self.stats["affection"] = max(0, min(100, self.stats["affection"]))

    char_dir = os.path.join("models", character_name)
    emotions_dir = os.path.join(char_dir, "Эмоции")
    actions_dir = os.path.join(char_dir, "Действия")
    animations_dir = os.path.join(char_dir, "Анимации")

    emotions = (
        os.listdir(emotions_dir) if os.path.exists(emotions_dir) else []
    )
    actions = os.listdir(actions_dir) if os.path.exists(actions_dir) else []
    animations = (
        os.listdir(animations_dir) if os.path.exists(animations_dir) else []
    )

    chosen_emotion = emotions[0] if emotions else "Пусто"
    chosen_anim = animations[0] if animations else "Пусто"
    triggered_action = None

    real_ai_response = self.call_real_api(
        model_name, api_url, api_key, user_text
    )

    if real_ai_response:
      dialogue = real_ai_response
      ConsoleLog.info(f"Получен реальный ответ от ИИ: '{dialogue[:50]}...'")
    else:
      dialogue = "Смотрит на тебя (ошибка связи с API)."
      ConsoleLog.error(
          "Не удалось получить ответ от API. Смотри красные логи выше!"
      )

    if self.stats["offense"] > 65:
      dialogue += " [Фыркает от обиды]"
      ConsoleLog.warn(f"Персонаж обижен! Текущая обида: {self.stats['offense']}")
      for e in emotions:
        if "злость" in e.lower() or "angry" in e.lower() or "обид" in e.lower():
          chosen_emotion = e
          break

      if actions and self.stats["offense"] > 80:
        triggered_action = random.choice(actions)
        dialogue += f" [Решил наказать тебя: '{triggered_action}']"
        ConsoleLog.warn(
            f"Критический уровень обиды! ИИ задействовал файл действия:"
            f" {triggered_action}"
        )
        self.execute_system_action(triggered_action)

    elif self.stats["affection"] > 70:
      for e in emotions:
        if (
            "улыб" in e.lower()
            or "smile" in e.lower()
            or "рад" in e.lower()
        ):
          chosen_emotion = e
          break

    return {
        "dialogue": dialogue,
        "emotion": chosen_emotion,
        "animation": chosen_anim,
        "action": triggered_action,
        "offense": self.stats["offense"],
    }

  def execute_system_action(self, action_name):
    name_lower = action_name.lower()
    try:
      if "выключить_пк" in name_lower or "shutdown" in name_lower:
        ConsoleLog.info("Сработала системная функция ИИ: Выключение ПК")
      elif "перезагруз" in name_lower or "reboot" in name_lower:
        ConsoleLog.info("Сработала системная функция ИИ: Перезагрузка")
      elif "браузер" in name_lower or "browser" in name_lower:
        os.startfile("https://www.google.com")
        ConsoleLog.info("Сработала системная функция ИИ: Открытие браузера")
      elif "закрыть" in name_lower or "close" in name_lower:
        ConsoleLog.info("Сработала системная функция ИИ: Закрыть окно")
    except Exception as e:
      ConsoleLog.error(f"Не удалось выполнить системное действие: {e}")


ai_brain = AICharacterBrain()


# ==========================================
# 3. ПЛАВАЮЩЕЕ ОКНО НА РАБОЧЕМ СТОЛЕ
# ==========================================
class DesktopOverlay(tk.Toplevel):

  def __init__(self, parent, character_name):
    super().__init__(parent)
    self.title(character_name)
    self.geometry("260x320+100+100")
    self.overrideredirect(True)
    self.attributes("-topmost", True)
    self.attributes("-alpha", 0.85)
    self.config(bg="#121212")
    ConsoleLog.info(
        f"Виджет персонажа '{character_name}' выведен на рабочий стол."
    )

    self.bind("<Button-1>", self.start_move)
    self.bind("<B1-Motion>", self.do_move)

    self.label_name = tk.Label(
        self,
        text=f"🤖 {character_name}",
        bg="#121212",
        fg="#00ffcc",
        font=("Arial", 11, "bold"),
    )
    self.label_name.pack(pady=10)

    self.speech_bubble = tk.Text(
        self,
        height=6,
        width=28,
        bg="#222222",
        fg="#ffffff",
        font=("Arial", 9),
        wrap="word",
        bd=0,
    )
    self.speech_bubble.pack(padx=10, pady=5)
    self.speech_bubble.insert(
        tk.END, "Привет! Я на рабочем столе. Можешь общаться со мной в панели."
    )
    self.speech_bubble.config(state="disabled")

    close_btn = tk.Button(
        self,
        text="Свернуть с экрана",
        command=self.destroy,
        bg="#333333",
        fg="#ffffff",
        bd=0,
        font=("Arial", 8),
    )
    close_btn.pack(pady=10)

  def start_move(self, event):
    self.x = event.x
    self.y = event.y

  def do_move(self, event):
    x = self.winfo_x() + (event.x - self.x)
    y = self.winfo_y() + (event.y - self.y)
    self.geometry(f"+{x}+{y}")

  def update_text(self, text):
    self.speech_bubble.config(state="normal")
    self.speech_bubble.delete("1.0", tk.END)
    self.speech_bubble.insert(tk.END, text)
    self.speech_bubble.config(state="disabled")

  def destroy(self):
    ConsoleLog.info("Виджет с рабочего стола был закрыт.")
    super().destroy()


# ==========================================
# 4. ГРАФИЧЕСКАЯ ПАНЕЛЬ УПРАВЛЕНИЯ
# ==========================================
class CharacterPanel(tk.Tk):

  def __init__(self):
    super().__init__()

    self.title("Панель управления ИИ-персонажем")
    self.geometry("640x880")
    self.config(bg="#1e1e1e")
    self.desktop_window = None
    ConsoleLog.info("Графическая панель управления запускается...")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "TLabel", background="#1e1e1e", foreground="#ffffff", font=("Arial", 10)
    )
    style.configure(
        "TButton", background="#333333", foreground="#ffffff", font=("Arial", 10)
    )

    ai_frame = tk.LabelFrame(
        self,
        text=" Настройки ИИ и API ",
        bg="#1e1e1e",
        fg="#ffffff",
        font=("Arial", 10, "bold"),
    )
    ai_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(ai_frame, text="Модель ИИ:").grid(
        row=0, column=0, sticky="w", padx=5, pady=5
    )
    self.model_combo = ttk.Combobox(
        ai_frame,
        values=["Google AI Studio", "DeepSeek", "GPT-4o", "Claude 3.5"],
        state="readonly",
    )
    self.model_combo.grid(row=0, column=1, padx=5, pady=5)
    self.model_combo.current(0)
    self.model_combo.bind("<<ComboboxSelected>>", self.on_model_change)

    ttk.Label(ai_frame, text="URL Адрес API:").grid(
        row=1, column=0, sticky="w", padx=5, pady=5
    )
    self.url_entry = ttk.Entry(ai_frame, width=35)
    self.url_entry.grid(row=1, column=1, padx=5, pady=5)
    self.url_entry.insert(
        0,
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
    )

    ttk.Label(ai_frame, text="API Ключ:").grid(
        row=2, column=0, sticky="w", padx=5, pady=5
    )
    self.key_entry = ttk.Entry(ai_frame, show="*", width=35)
    self.key_entry.grid(row=2, column=1, padx=5, pady=5)

    selection_frame = tk.LabelFrame(
        self,
        text=" Персонаж и Озвучка ",
        bg="#1e1e1e",
        fg="#ffffff",
        font=("Arial", 10, "bold"),
    )
    selection_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(selection_frame, text="Персонаж (из models/):").grid(
        row=0, column=0, sticky="w", padx=5, pady=5
    )
    self.char_combo = ttk.Combobox(selection_frame, state="readonly")
    self.char_combo.grid(row=0, column=1, padx=5, pady=5)

    add_char_btn = ttk.Button(
        selection_frame, text="+ Добавить модель", command=self.add_new_model
    )
    add_char_btn.grid(row=0, column=2, padx=5, pady=5)

    desktop_btn = ttk.Button(
        selection_frame,
        text="🖥 Переместить на рабочий стол",
        command=self.spawn_to_desktop,
    )
    desktop_btn.grid(row=1, column=0, columnspan=3, sticky="we", padx=5, pady=5)

    ttk.Label(selection_frame, text="Голос (.mp3 из voices/):").grid(
        row=2, column=0, sticky="w", padx=5, pady=5
    )
    self.voice_combo = ttk.Combobox(selection_frame, state="readonly")
    self.voice_combo.grid(row=2, column=1, padx=5, pady=5)

    self.refresh_dropdowns()

    chat_frame = tk.LabelFrame(
        self,
        text=" Чат с персонажем ",
        bg="#1e1e1e",
        fg="#ffffff",
        font=("Arial", 10, "bold"),
    )
    chat_frame.pack(fill="both", expand=True, padx=10, pady=5)

    self.chat_history = tk.Text(
        chat_frame,
        bg="#2d2d2d",
        fg="#ffffff",
        insertbackground="white",
        font=("Arial", 10),
        height=10,
    )
    self.chat_history.pack(fill="both", expand=True, padx=5, pady=5)
    self.chat_history.insert(
        tk.END,
        "Система: Панель запущена. Ключ и настройки сохраняются автоматически.\n",
    )

    input_frame = tk.Frame(chat_frame, bg="#1e1e1e")
    input_frame.pack(fill="x", padx=5, pady=5)

    self.msg_entry = ttk.Entry(input_frame, font=("Arial", 10))
    self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
    self.msg_entry.bind("<Return>", lambda event: self.send_message())

    send_btn = ttk.Button(
        input_frame, text="Отправить", command=self.send_message
    )
    send_btn.pack(side="right")

    # Загружаем сохраненный ключ и настройки при старте
    self.load_config()

    # Перехватываем закрытие окна, чтобы сохранить данные
    self.protocol("WM_DELETE_WINDOW", self.on_close)

    ConsoleLog.info("Панель управления успешно отрисована.")

  def on_model_change(self, event):
    selected_model = self.model_combo.get()
    self.url_entry.delete(0, tk.END)
    if "Google" in selected_model:
      self.url_entry.insert(
          0,
          "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
      )
    elif "DeepSeek" in selected_model:
      self.url_entry.insert(0, "https://api.deepseek.com/v1/chat/completions")
    elif "GPT" in selected_model:
      self.url_entry.insert(0, "https://api.openai.com/v1/chat/completions")
    ConsoleLog.info(f"Смена шаблона URL для модели: {selected_model}")

  def refresh_dropdowns(self):
    models_path = "models"
    available_chars = (
        [
            d
            for d in os.listdir(models_path)
            if os.path.isdir(os.path.join(models_path, d))
        ]
        if os.path.exists(models_path)
        else []
    )
    if not available_chars:
      available_chars = ["Папка models пуста"]
      ConsoleLog.warn("Папка models/ пуста. Нет доступных персонажей.")

    self.char_combo["values"] = available_chars
    if available_chars and "Папка models пуста" not in available_chars:
      self.char_combo.current(0)
    else:
      self.char_combo.set("Папка models пуста")

    voices_path = "voices"
    available_voices = (
        [
            f
            for f in os.listdir(voices_path)
            if f.lower().endswith(".mp3")
            and os.path.isfile(os.path.join(voices_path, f))
        ]
        if os.path.exists(voices_path)
        else []
    )
    if not available_voices:
      available_voices = ["Голосов нет (текст пойдет в облачко)"]
      ConsoleLog.warn("Папка voices/ пуста. Озвучка отключена.")

    self.voice_combo["values"] = available_voices
    self.voice_combo.current(0)

  def add_new_model(self):
    new_name = simpledialog.askstring(
        "Новая модель", "Введите имя нового персонажа:"
    )
    if new_name:
      new_name = new_name.strip()
      char_path = os.path.join("models", new_name)
      try:
        if not os.path.exists(char_path):
          os.makedirs(char_path)
          for sub in ["Эмоции", "Действия", "Анимации"]:
            os.makedirs(os.path.join(char_path, sub))
          ConsoleLog.info(
              f"Успешно создана новая модель '{new_name}' с подпапками."
          )
        else:
          ConsoleLog.warn(
              f"Попытка создать существующую модель '{new_name}'."
          )

        messagebox.showinfo(
            "Успех", f"Папка персонажа '{new_name}' создана в models/!"
        )
        self.refresh_dropdowns()
        self.char_combo.set(new_name)
      except Exception as e:
        ConsoleLog.error(f"Не удалось создать модель '{new_name}': {e}")
        messagebox.showerror("Ошибка", f"Не удалось создать папку: {e}")

  def spawn_to_desktop(self):
    current_char = self.char_combo.get()
    if "пуста" in current_char:
      ConsoleLog.warn(
          "Попытка вывода на рабочий стол при пустой папке персонажей."
      )
      messagebox.showwarning("Ошибка", "Сначала добавьте модель через кнопку!")
      return

    if self.desktop_window is not None and self.desktop_window.winfo_exists():
      self.desktop_window.destroy()

    self.desktop_window = DesktopOverlay(self, current_char)
    self.log_chat(
        "Система", f"Персонаж '{current_char}' перемещен на рабочий стол."
    )

  def log_chat(self, sender, text):
    self.chat_history.insert(tk.END, f"{sender}: {text}\n")
    self.chat_history.see(tk.END)

  def save_config(self):
    """Сохраняет текущие настройки и API-ключ в файл config.json"""
    config_data = {
        "model": self.model_combo.get(),
        "url": self.url_entry.get(),
        "key": self.key_entry.get(),
        "character": self.char_combo.get(),
        "voice": self.voice_combo.get(),
    }
    try:
      with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)
      ConsoleLog.info("Настройки и API-ключ успешно сохранены.")
    except Exception as e:
      ConsoleLog.error(f"Не удалось сохранить конфиг: {e}")

  def load_config(self):
    """Загружает сохраненные настройки и API-ключ из файла config.json"""
    if os.path.exists(CONFIG_FILE):
      try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
          config_data = json.load(f)

          if "model" in config_data:
            self.model_combo.set(config_data["model"])
          if "url" in config_data:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, config_data["url"])
          if "key" in config_data:
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, config_data["key"])
          if "character" in config_data and config_data["character"] in self.char_combo["values"]:
            self.char_combo.set(config_data["character"])
          if "voice" in config_data and config_data["voice"] in self.voice_combo["values"]:
            self.voice_combo.set(config_data["voice"])

        ConsoleLog.info("Настройки и API-ключ загружены из файла.")
      except Exception as e:
        ConsoleLog.error(f"Не удалось загрузить конфиг: {e}")

  def on_close(self):
    """Вызывается при закрытии окна программы"""
    self.save_config()
    if self.desktop_window is not None and self.desktop_window.winfo_exists():
      self.desktop_window.destroy()
    ConsoleLog.info("Приложение закрывается.")
    self.destroy()

  def send_message(self):
    user_text = self.msg_entry.get().strip()
    if not user_text:
      return

    api_url = self.url_entry.get().strip()
    api_key = self.key_entry.get().strip()
    model_name = self.model_combo.get()

    if not api_url or not api_key:
      ConsoleLog.warn(
          "Попытка отправки сообщения без заполненного URL или API ключа."
      )
      messagebox.showwarning("Внимание", "Заполни URL адрес и API ключ!")
      return

    # Сохраняем конфиг при отправке сообщения (на всякий случай)
    self.save_config()

    self.log_chat("Вы", user_text)
    ConsoleLog.info(f"Пользователь отправил сообщение: '{user_text}'")
    self.msg_entry.delete(0, tk.END)

    current_char = self.char_combo.get()
    selected_voice = self.voice_combo.get()

    if "пуста" in current_char:
      ConsoleLog.error("Ошибка чата: не выбран персонаж.")
      messagebox.showwarning("Ошибка", "Сначала добавьте модель!")
      return

    result = ai_brain.evaluate_and_act(
        current_char, user_text, model_name, api_url, api_key
    )
    response_text = result["dialogue"]

    if self.desktop_window is not None and self.desktop_window.winfo_exists():
      self.desktop_window.update_text(response_text)

    if "нет" in selected_voice or not selected_voice:
      response_text += " 💬 [Голос не добавлен -> Текст выведен в облачко]"
      ConsoleLog.info("Озвучка пропущена: файл голоса не выбран.")
    else:
      response_text += f" 🔊 [Озвучено через голос: {selected_voice}]"
      ConsoleLog.info(f"Используется голос для озвучки: {selected_voice}")

    debug_folders = (
        f"(ИИ прочитал у {current_char}: Эмоция -> {result['emotion']},"
        f" Анимация -> {result['animation']})"
    )
    self.log_chat(current_char, f"{response_text}\n{debug_folders}")
    ConsoleLog.info(f"Ответ персонажа '{current_char}' успешно выведен.")


if __name__ == "__main__":
  ConsoleLog.info("Запуск приложения...")
  app = CharacterPanel()
  app.mainloop()