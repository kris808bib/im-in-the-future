from config import PROFESSIONS, COLOR_PALETTE

class CharacterModel:
    def __init__(self):
        self.current_character = {
            "gender": "male",
            "hair_style": "side_part",
            "hair_color": "blonde",
            "eyes": "round",
            "eyes_color": "blue",
            "skin_color": "light",
            "pose": "half",
            "profession": "control_engineer"
        }
        
        self.professions = PROFESSIONS
        self.color_palette = COLOR_PALETTE

    def update_parameter(self, param, value):
        self.current_character[param] = value

    def build_prompt(self):
        gender = "мужчины" if self.current_character["gender"] == "male" else "женщины"
        hair_style_map = {
            "side_part": "короткая стрижка с боковым пробором",
            "bob": "мужская стрижка боб",
            "medium": "средняя длина волос по плечи",
            "long_curly": "длинные кудрявые волосы",
            "long_straight": "длинные прямые волосы"
        }
        profession_bg = self.professions[self.current_character["profession"]]["background"]
        
        return (
            f"Изображение {gender}, {self._get_skin_color()}, "
            f"{hair_style_map[self.current_character['hair_style']]}, "
            f"{self._get_hair_color()} волосы, {self._get_eyes()}, "
            f"{profession_bg}, стоит на фоне лаборатории, он счастив, стиль аниме, высокое качество"
        )

    def _get_skin_color(self):
        return {
            "light": "светлая кожа",
            "medium": "средний цвет кожи",
            "dark": "темная кожа"
        }[self.current_character["skin_color"]]

    def _get_hair_color(self):
        return {
            "blonde": "светлые",
            "light_brown": "русые",
            "brown": "каштановые",
            "red": "рыжие"
        }[self.current_character["hair_color"]]

    def _get_eyes(self):
        return {
            "round": "круглые глаза",
            "almond": "узкие глаза"
        }[self.current_character["eyes"]]