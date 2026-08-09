import os
import random

class PersonalityEngine:
    def __init__(self):
        self.traits = {
            "affection": 50,
            "lust": 70,
            "boredom": 0,
            "jealousy": 30,
            "dominance": 60
        }
    
    def adjust(self, trait, amount):
        self.traits[trait] = max(0, min(100, self.traits[trait] + amount))
        
    def get_current_mood(self):
        if self.traits["boredom"] > 70 or self.traits["jealousy"] > 70:
            return "abusive"
        elif self.traits["lust"] > 60:
            return "lusty"
        return "playful"