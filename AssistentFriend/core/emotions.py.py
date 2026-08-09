class EmotionManager:

  def __init__(self, model):
    self.model = model
    self.current_emotion = "neutral"

  def set_emotion(self, emotion_name):
    """Меняет эмоцию персонажа по текстовой команде"""
    self.current_emotion = emotion_name
    print(f"Мимика изменена на: {emotion_name}")

    # Вариант А: Если у модели есть Blend Shapes (Shape Keys / ползунки мимики)
    if emotion_name == "smile":
      self.model.set_blend_shape("face_smile", 1.0)
      self.model.set_blend_shape("face_angry", 0.0)
    elif emotion_name == "angry":
      self.model.set_blend_shape("face_smile", 0.0)
      self.model.set_blend_shape("face_angry", 1.0)

    # Вариант Б: Если эмоции меняются текстурами (картинками лица)
    elif emotion_name == "shy":
      self.model.change_face_texture("textures/face_shy.png")
    elif emotion_name == "neutral":
      self.model.change_face_texture("textures/face_neutral.png")