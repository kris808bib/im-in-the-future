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
            "profession": "control_engineer",
            "accessories": {
                "glasses": "none",
                "headwear": "none",
                "facial": "none"
            }
        }

        self.professions = PROFESSIONS
        self.color_palette = COLOR_PALETTE
        self.accessories_categories = {
            "glasses": ["none", "oval_glasses", "basic_glasses", "circle_glasses", "rect_glasses"],
            "headwear": ["none", "cap", "bonnet", "hat", "beret"],
            "facial": ["none", "beard", "moustache"]
        }

    def update_parameter(self, param, value):
        self.current_character[param] = value

    def update_accessory(self, category, value):
        self.current_character["accessories"][category] = value

    def build_prompt(self):
        gender = "мужчины" if self.current_character["gender"] == "male" else "женщины"
        hair_style_map = {
            "side_part": "короткая стрижка с боковым пробором",
            "bob": "мужская стрижка боб",
            "medium": "средняя длина волос по плечи",
            "long_curly": "длинные кудрявые волосы",
            "long_straight": "длинные прямые волосы",
            "afro": "пышные афроволосы",
            "smalllong_men's_hair": "удлиненная мужская стрижка",
            "supershort_men's_hair": "очень короткая стрижка под машинку",
            "braids": "волосы заплетены в две косы",
            "two_tail": "волосы собраны в два хвоста",
            "long_tail": "Высокий длинный хвост",
            "men's_braids": "африканские косички",
            # "fringe": "стижка с челкой",
            "bunch": "пучок, собранный на голове",
            "piksi": "стрижка пикси",
            "bald": "лысый без волос, волосы отсутсвуют, видна блестящая кожа головы"
        }

        profession_bg = self.professions[self.current_character["profession"]]["background"]
        accessories_desc = self._get_accessories_description()

        return (
            f"Изображение {gender}, {self._get_skin_color()}, "
            f"{hair_style_map[self.current_character['hair_style']]}, "
            f"{self._get_hair_color()} цвет волос, {self._get_eyes()} цвет глаз, "
            f"{accessories_desc}, "
            f"{profession_bg}, стоит на фоне лаборатории, он счастлив, стиль аниме, высокое качество"
        )

    def _get_skin_color(self):
        return {
            "light": "светлая европейская кожа",
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


    def _get_accessories_description(self):
        descriptions = {
            "glasses": {
                "none": "без очков",
                "oval_glasses": "с овальными очками встиле бренда miu miu",
                "basic_glasses": "с обычными очками",
                "circle_glasses": "с очками круглой формы, как у гарри поттера",
                "rect_glasses": "с очками прямойгольноый формы, имеющими четкую форму"
            },
            "headwear": {
                "none": "без головного убора",
                "cap": "в кепке",
                "bonnet": "в шляпе с шировкими полями",
                "hat": "в вязанной шапке",
                "beret": "в берете во французском стиле",
                "sport": "в спортивной повязке для бега "
            },
            "facial": {
                "none": "",
                "beard": "с бородой",
                "moustache": "с усами под носом"
            }
        }
        
        parts = []
        for category, item in self.current_character["accessories"].items():
            desc = descriptions[category].get(item, "")
            if desc:  # Добавляем только непустые описания
                parts.append(desc)
        
        return " ".join(parts) if parts else "без аксессуаров"

    def _get_accessory_name(self, accessory):
        names = {
            "oval_glasses": "овальные очки",
            "basic_glasses": "обычные очки",
            "circle_glasses": "круглые очки",
            "rect_glasses": "прямоугольные очки",
            "cap": "кепка",
            "bonnet": "шляпа",
            "hat": "шапка",
            "beret": "берет",
            "beard": "борода",
            "moustache": "усы"
        }
        return names.get(accessory, "")