import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import json
import io
import base64
import os
import time 


class CharacterCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конструктор будущего инженера")
        self.root.geometry("1200x800")
        
        # API конфигурация (в реальном приложении храните это безопасно!)
        self.API_URL = "https://api-key.fusionbrain.ai/"
        self.API_KEY = "8AF886A5D68CEB8B4263A24D76B3B6A3"  # Замените на реальный ключ
        self.SECRET_KEY = "DB4FB8D7263008BD65BEB0367F9D0A9E"  # Замените на реальный ключ
        self.pipeline_id = None
        
        # Загрузки изображений для предпросмотра
        self.load_assets()
        
        # Текущий персонаж
        self.current_character = {
            "gender": "male",
            "hair_style": "short",
            "hair_color": "black",
            "eyes": "round",
            "eyes_color": "brown",
            "profession": "control_engineer"
        }
        
        # Описания профессий
        self.professions = {
            "control_engineer": {
                "name": "Инженер АСУ ТП",
                "description": "Разработка автоматизированных систем управления технологическими процессами"
            },
            "robotics_engineer": {
                "name": "Инженер-робототехник",
                "description": "Проектирование и программирование промышленных роботов"
            },
            "quality_engineer": {
                "name": "Инженер по качеству",
                "description": "Контроль качества продукции и процессов"
            }
        }
        
        self.setup_ui()
        self.connect_to_api()
    
    def load_assets(self):
        """Загрузка изображений для предпросмотра"""
        self.images = {
            "male": self.load_image("assets/male.png"),
            "female": self.load_image("assets/female.png"),
            "short": self.load_image("assets/hair_short.png"),
            "long": self.load_image("assets/hair_long.png"),
            "black": self.load_image("assets/color_black.png"),
            "blonde": self.load_image("assets/color_blonde.png"),
            "round": self.load_image("assets/eyes_round.png"),
            "almond": self.load_image("assets/eyes_almond.png"),
            "brown": self.load_image("assets/eyes_brown.png"),
            "blue": self.load_image("assets/eyes_blue.png"),
            "default": self.load_image("assets/default_character.png")
        }
    
    def load_image(self, path, size=(50, 50)):
        """Загрузка и масштабирование изображения"""
        try:
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except:
            # Заглушка если изображение не найдено
            blank = Image.new('RGB', size, color='gray')
            return ImageTk.PhotoImage(blank)
    
    def connect_to_api(self):
        """Подключение к FusionBrain API"""
        try:
            headers = {
                'X-Key': f'Key {self.API_KEY}',
                'X-Secret': f'Secret {self.SECRET_KEY}',
            }
            response = requests.get(self.API_URL + 'key/api/v1/pipelines', headers=headers)
            self.pipeline_id = response.json()[0]['id']
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к API: {str(e)}")
    
    def generate_character_image(self, prompt):
        """Генерация изображения через API"""
        if not self.pipeline_id:
            messagebox.showerror("Ошибка", "API не подключено")
            return None
        
        try:
            # Подготовка параметров
            params = {
                "type": "GENERATE",
                "numImages": 1,
                "width": 512,
                "height": 512,
                "generateParams": {
                    "query": prompt
                }
            }
            
            data = {
                'pipeline_id': (None, self.pipeline_id),
                'params': (None, json.dumps(params), 'application/json')
            }
            
            headers = {
                'X-Key': f'Key {self.API_KEY}',
                'X-Secret': f'Secret {self.SECRET_KEY}',
            }
            
            # Отправка запроса
            response = requests.post(
                self.API_URL + 'key/api/v1/pipeline/run',
                headers=headers,
                files=data
            )
            task_id = response.json()['uuid']
            
            # Проверка статуса
            for _ in range(10):
                status_response = requests.get(
                    self.API_URL + 'key/api/v1/pipeline/status/' + task_id,
                    headers=headers
                )
                status = status_response.json()
                
                if status['status'] == 'DONE':
                    return status['result']['files'][0]
                elif status['status'] == 'FAIL':
                    raise Exception("Ошибка генерации изображения")
                
                self.root.update()
                time.sleep(5)
            
            raise Exception("Превышено время ожидания")
            
        except Exception as e:
            print(e)
            messagebox.showerror("Ошибка", f"Ошибка генерации: {str(e)}")
            return None
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - выбор характеристик
        options_frame = ttk.Frame(main_frame, width=400)
        options_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Правая панель - предпросмотр
        preview_frame = ttk.Frame(main_frame)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Настройка характеристик
        self.setup_gender_selection(options_frame)
        self.setup_hair_selection(options_frame)
        self.setup_eyes_selection(options_frame)
        self.setup_profession_selection(options_frame)
        
        # Кнопка генерации
        ttk.Button(
            options_frame, 
            text="Сгенерировать персонажа", 
            command=self.generate_full_character
        ).pack(pady=20)
        
        # Область предпросмотра
        self.preview_label = ttk.Label(preview_frame, image=self.images["default"])
        self.preview_label.pack(pady=20)
        
        # Описание профессии
        self.profession_desc = tk.StringVar()
        ttk.Label(
            preview_frame, 
            textvariable=self.profession_desc,
            wraplength=400,
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Обновляем описание
        self.update_profession_description()
    
    def setup_gender_selection(self, parent):
        """Выбор пола персонажа"""
        frame = ttk.LabelFrame(parent, text="Пол", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.gender_var = tk.StringVar(value="male")
        
        male_frame = ttk.Frame(frame)
        male_frame.pack(side=tk.LEFT, expand=True)
        ttk.Radiobutton(
            male_frame,
            image=self.images["male"],
            variable=self.gender_var,
            value="male",
            command=self.update_preview
        ).pack()
        ttk.Label(male_frame, text="Мужской").pack()
        
        female_frame = ttk.Frame(frame)
        female_frame.pack(side=tk.LEFT, expand=True)
        ttk.Radiobutton(
            female_frame,
            image=self.images["female"],
            variable=self.gender_var,
            value="female",
            command=self.update_preview
        ).pack()
        ttk.Label(female_frame, text="Женский").pack()
    
    def setup_hair_selection(self, parent):
        """Выбор прически и цвета волос"""
        # Стиль прически
        frame = ttk.LabelFrame(parent, text="Прическа", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.hair_style_var = tk.StringVar(value="short")
        
        short_frame = ttk.Frame(frame)
        short_frame.pack(side=tk.LEFT, expand=True)
        ttk.Radiobutton(
            short_frame,
            image=self.images["short"],
            variable=self.hair_style_var,
            value="short",
            command=self.update_preview
        ).pack()
        ttk.Label(short_frame, text="Короткая").pack()
        
        long_frame = ttk.Frame(frame)
        long_frame.pack(side=tk.LEFT, expand=True)
        ttk.Radiobutton(
            long_frame,
            image=self.images["long"],
            variable=self.hair_style_var,
            value="long",
            command=self.update_preview
        ).pack()
        ttk.Label(long_frame, text="Длинная").pack()
        
        # Цвет волос
        frame = ttk.LabelFrame(parent, text="Цвет волос", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.hair_color_var = tk.StringVar(value="black")
        
        black_frame = ttk.Frame(frame)
        black_frame.pack(side=tk.LEFT, expand=True)
        ttk.Radiobutton(
            black_frame,
            image=self.images["black"],
            variable=self.hair_color_var,
            value="black",
            command=self.update_preview
        ).pack()
        ttk.Label(black_frame, text="Черный").pack()
        
        blonde_frame = ttk.Frame(frame)
        blonde_frame.pack(side=tk.LEFT, expand=True)
        ttk.Radiobutton(
            blonde_frame,
            image=self.images["blonde"],
            variable=self.hair_color_var,
            value="blonde",
            command=self.update_preview
        ).pack()
        ttk.Label(blonde_frame, text="Светлый").pack()
    
    def setup_eyes_selection(self, parent):
        """Выбор формы и цвета глаз"""
        # Форма глаз
        frame = ttk.LabelFrame(parent, text="Форма глаз", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.eyes_var = tk.StringVar(value="round")
        
        round_frame = ttk.Frame(frame)
        round_frame.pack(side=tk.LEFT, expand=True)
        ttk.Radiobutton(
            round_frame,
            image=self.images["round"],
            variable=self.eyes_var,
            value="round",
            command=self.update_preview
        ).pack()
        ttk.Label(round_frame, text="Круглые").pack()
        
        almond_frame = ttk.Frame(frame)
        almond_frame.pack(side=tk.LEFT, expand=True)
        ttk.Radiobutton(
            almond_frame,
            image=self.images["almond"],
            variable=self.eyes_var,
            value="almond",
            command=self.update_preview
        ).pack()
        ttk.Label(almond_frame, text="Миндалевидные").pack()
        
        # Цвет глаз
        frame = ttk.LabelFrame(parent, text="Цвет глаз", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.eyes_color_var = tk.StringVar(value="brown")
        
        brown_frame = ttk.Frame(frame)
        brown_frame.pack(side=tk.LEFT, expand=True)
        ttk.Radiobutton(
            brown_frame,
            image=self.images["brown"],
            variable=self.eyes_color_var,
            value="brown",
            command=self.update_preview
        ).pack()
        ttk.Label(brown_frame, text="Карие").pack()
        
        blue_frame = ttk.Frame(frame)
        blue_frame.pack(side=tk.LEFT, expand=True)
        ttk.Radiobutton(
            blue_frame,
            image=self.images["blue"],
            variable=self.eyes_color_var,
            value="blue",
            command=self.update_preview
        ).pack()
        ttk.Label(blue_frame, text="Голубые").pack()
    
    def setup_profession_selection(self, parent):
        """Выбор профессии"""
        frame = ttk.LabelFrame(parent, text="Профессия", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.profession_var = tk.StringVar(value="control_engineer")
        
        for key, prof in self.professions.items():
            btn = ttk.Radiobutton(
                frame,
                text=prof["name"],
                variable=self.profession_var,
                value=key,
                command=self.update_profession_description
            )
            btn.pack(anchor=tk.W)
    
    def update_preview(self):
        """Обновление предпросмотра на основе выбранных параметров"""
        # В реальном приложении здесь можно собирать композицию из выбранных элементов
        self.preview_label.config(image=self.images["default"])
    
    def update_profession_description(self):
        """Обновление описания профессии"""
        prof = self.professions[self.profession_var.get()]
        self.profession_desc.set(f"{prof['name']}\n\n{prof['description']}")
    
    def generate_full_character(self):
        """Генерация полного персонажа"""
        # Собираем промт на основе выбранных параметров
        gender = "мужчина" if self.gender_var.get() == "male" else "женщина"
        
        hair_style_map = {
            "short": "короткие волосы",
            "long": "длинные волосы"
        }
        hair_style = hair_style_map[self.hair_style_var.get()]
        
        hair_color_map = {
            "black": "черные",
            "blonde": "светлые"
        }
        hair_color = hair_color_map[self.hair_color_var.get()]
        
        eyes_map = {
            "round": "круглые глаза",
            "almond": "миндалевидные глаза"
        }
        eyes = eyes_map[self.eyes_var.get()]
        
        eyes_color_map = {
            "brown": "карие",
            "blue": "голубые"
        }
        eyes_color = eyes_color_map[self.eyes_color_var.get()]
        
        profession_map = {
            "control_engineer": "скада система",
            "robotics_engineer": "современные роботизированные установки",
            "quality_engineer": "инженер по контролю качества"
        }
        profession = profession_map[self.profession_var.get()]
        
        prompt = (
            f"Изображение {gender} до пояса, {hair_style}, {hair_color}, {eyes}, {eyes_color}, "
            f"на фоне {profession}, реалистичный стиль, высокое качество"
        )
        print(prompt)
        # Показываем сообщение о генерации
        self.preview_label.config(text="Генерация изображения...")
        self.root.update()
        
        # Генерируем изображение
        image_data = self.generate_character_image(prompt)
        
        if image_data:
            self.display_generated_image(image_data)
    
    def display_generated_image(self, image_base64):
        """Отображение сгенерированного изображения"""
        try:
            # Декодируем base64
            image_data = base64.b64decode(image_base64)
            
            # Создаем изображение PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Масштабируем для отображения
            image.thumbnail((500, 500))
            photo = ImageTk.PhotoImage(image)
            
            # Обновляем превью
            self.preview_label.config(image=photo)
            self.preview_label.image = photo
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отобразить изображение: {str(e)}")
            self.preview_label.config(image=self.images["default"])

if __name__ == "__main__":
    root = tk.Tk()
    app = CharacterCreatorApp(root)
    root.mainloop()