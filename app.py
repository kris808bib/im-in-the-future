import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import requests
import json
import io
import base64
import time
import threading
import os


class CharacterCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конструктор будущего инженера")
        self.root.geometry("1200x800")
        self.logo_path = "assets\logo.png"  # Укажите правильный путь
        self.logo_size = (50, 50) 
        
        # API конфигурация
        self.API_URL = "https://api-key.fusionbrain.ai/"
        self.API_KEY = "8AF886A5D68CEB8B4263A24D76B3B6A3"
        self.SECRET_KEY = "DB4FB8D7263008BD65BEB0367F9D0A9E"
        self.pipeline_id = None
        self.cancel_flag = False
        
        # Загрузка изображений
        self.load_images()
        
        # Текущий персонаж
        self.current_character = {
            "gender": "male",
            "hair_style": "side_part",
            "hair_color": "blonde",
            "eyes": "round",
            "eyes_color": "blue",
            "skin_color": "light",
            "pose": "half",
            "profession": "control_engineer",
            "style": "realistic"
        }
        
        # Профессии и соответствующие фоны
        self.professions = {
            "control_engineer": {
                "name": "Инженер АСУ ТП",
                "background": "Инженер АСУ ТП (автоматизированных систем управления технологическими процессами)  выбирает необходимые датчики, контроллеры, средства связи и другое оборудование для реализации системы,"
            },
            "robotics_engineer": {
                "name": "Инженер-робототехник",
                "background": "профессия инженер-робототехник, она стоит на предприятии и в данный момент проектирует и обслуживает робота "
            },
            "software_engineer": {
                "name": "Инженер-программист",
                "background": "профессия инженер-программист, в руках ноутбук на котором она пишет код и она стоит сидит в офисе"
            },
            "ai_specialist": {
                "name": "Cпециалист по искусственному интеллекту",
                "background": "профессия специалист по искусственному интеллекту занимается программированием на своем ноутбуке разработкой, тестированием и внедрением программ и систем, использующих алгоритмы искусственного интеллекта"
            }
        }
        
        # Цвета волос, глаз и кожи
        self.hair_colors = {
            "blonde": "#F5E6C4",
            "light_brown": "#B57A4F",
            "brown": "#5A3825",
            "red": "#A53A2E"
        }
        
        self.eye_colors = {
            "blue": "#87CEEB",
            "green": "#2E8B57",
            "brown": "#654321"
        }
        
        self.skin_colors = {
            "light": "#FFDBAC",
            "medium": "#E5BA8F",
            "dark": "#C68642"
        }
        
        self.setup_ui()
        self.connect_to_api()
    
    def load_images(self):
        """Загрузка изображений для интерфейса"""
        # Создаем папку для изображений, если её нет
        if not os.path.exists("assets"):
            os.makedirs("assets")
        
        # Изображения причесок
        self.hair_images = {
            "side_part": self.load_image("assets/hair_short.png", (100, 100)),
            "bob": self.load_image("assets/hair_bob.png", (100, 100)),
            "medium": self.load_image("assets/hair_medium.png", (100, 100)),
            "long_curly": self.load_image("assets/hair_long_curly.png", (100, 100)),
            "long_straight": self.load_image("assets/hair_long_straight.png", (100, 100))
        }
        
        # Изображения форм глаз
        self.eyes_images = {
            "round": self.load_image("assets/eyes_round.png", (80, 40)),
            "almond": self.load_image("assets/eyes_almond.png", (80, 30))
        }
        
        # Заглушка для превью
        self.default_preview = self.create_sample_image("default", (400, 400), "#EEEEEE")
    
    def load_image(self, path, size):
        """Загрузка и масштабирование изображения"""
        try:
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except FileNotFoundError:
            return self.create_sample_image(os.path.basename(path).split('.')[0], size, "#CCCCCC")
        except Exception as e:
            print(f"Ошибка загрузки изображения {path}: {str(e)}")
            return self.create_sample_image("error", size, "#FFCCCC")
    
    def create_sample_image(self, name, size, color):
        """Создание временных изображений"""
        img = Image.new('RGB', size, color=color)
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), name, fill="black")
        return ImageTk.PhotoImage(img)
    
    def create_color_circle(self, color, size=30):
        """Создание круга с цветом"""
        img = Image.new('RGB', (size, size), color='white')
        draw = ImageDraw.Draw(img)
        draw.ellipse((2, 2, size-2, size-2), fill=color)
        return ImageTk.PhotoImage(img)
    
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
            
            response = requests.post(
                self.API_URL + 'key/api/v1/pipeline/run',
                headers=headers,
                files=data
            )
            task_id = response.json()['uuid']
            
            for _ in range(15):
                if self.cancel_flag:
                    self.cancel_flag = False
                    raise Exception("Генерация отменена")
                
                status_response = requests.get(
                    self.API_URL + 'key/api/v1/pipeline/status/' + task_id,
                    headers=headers
                )
                status = status_response.json()
                
                if status['status'] == 'DONE':
                    return status['result']['files'][0]
                elif status['status'] == 'FAIL':
                    raise Exception("Ошибка генерации изображения")
                
                time.sleep(10)
            
            raise Exception("Превышено время ожидания генерации (150 секунд)")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка сети: {str(e)}")
        except KeyError as e:
            raise Exception(f"Некорректный ответ API: {str(e)}")
        except Exception as e:
            raise Exception(f"Ошибка генерации: {str(e)}")
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - выбор характеристик (с прокруткой)
        left_container = ttk.Frame(main_frame)
        left_container.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        canvas = tk.Canvas(left_container)
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Правая панель - кнопка генерации и превью
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Кнопка генерации
        self.generate_btn = ttk.Button(
            right_frame, 
            text="Сгенерировать персонажа", 
            command=self.start_generation_thread,
            style='Accent.TButton'
        )
        self.generate_btn.pack(pady=20, ipadx=20, ipady=10)
        
        # Прогресс-бар (изначально скрыт)
        self.progress = ttk.Progressbar(
            right_frame,
            orient='horizontal',
            mode='indeterminate',
            length=400
        )
        
        # Область предпросмотра
        self.preview_label = ttk.Label(
            right_frame, 
            image=self.default_preview,
            text="Здесь будет изображение",
            compound='center',
            font=('Helvetica', 14),
            anchor='center'
        )
        self.preview_label.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # Настройка стиля
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Helvetica', 12, 'bold'))
        
        # Настройка характеристик
        self.setup_gender_selection(scrollable_frame)
        self.setup_skin_color_selection(scrollable_frame)
        self.setup_hair_selection(scrollable_frame)
        self.setup_eyes_selection(scrollable_frame)
        self.setup_pose_selection(scrollable_frame)
        self.setup_profession_selection(scrollable_frame)
        # self.setup_style_selection(scrollable_frame)
    
    def setup_gender_selection(self, parent):
        """Выбор пола персонажа"""
        frame = ttk.LabelFrame(parent, text="Пол", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.gender_var = tk.StringVar(value="male")
        
        male_frame = ttk.Frame(frame)
        male_frame.pack(side=tk.LEFT, expand=True)
        ttk.Radiobutton(
            male_frame,
            text="Мужской",
            variable=self.gender_var,
            value="male"
        ).pack()
        
        female_frame = ttk.Frame(frame)
        female_frame.pack(side=tk.LEFT, expand=True)
        ttk.Radiobutton(
            female_frame,
            text="Женский",
            variable=self.gender_var,
            value="female"
        ).pack()
    
    def setup_skin_color_selection(self, parent):
        """Выбор цвета кожи"""
        frame = ttk.LabelFrame(parent, text="Цвет кожи", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.skin_color_var = tk.StringVar(value="light")
        
        color_frame = ttk.Frame(frame)
        color_frame.pack()
        
        for name, color in self.skin_colors.items():
            frame_color = ttk.Frame(color_frame)
            frame_color.pack(side=tk.LEFT, padx=5)
            
            color_img = self.create_color_circle(color, 40)
            label = ttk.Label(frame_color, image=color_img)
            label.image = color_img
            label.pack()
            
            ttk.Radiobutton(
                frame_color,
                text=name.capitalize(),
                variable=self.skin_color_var,
                value=name
            ).pack()
    
    def setup_hair_selection(self, parent):
        """Выбор прически с изображениями"""
        frame = ttk.LabelFrame(parent, text="Прическа", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.hair_style_var = tk.StringVar(value="side_part")
        
        # Сетка для изображений причесок
        hair_grid = ttk.Frame(frame)
        hair_grid.pack()
        
        # Мужские прически
        male_frame = ttk.Frame(hair_grid)
        male_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(male_frame, text="Мужские", font=('Helvetica', 10, 'bold')).pack()
        
        ttk.Radiobutton(
            male_frame,
            image=self.hair_images["side_part"],
            variable=self.hair_style_var,
            value="side_part"
        ).pack(pady=5)
        
        ttk.Radiobutton(
            male_frame,
            image=self.hair_images["bob"],
            variable=self.hair_style_var,
            value="bob"
        ).pack(pady=5)
        
        # Женские прически
        female_frame = ttk.Frame(hair_grid)
        female_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(female_frame, text="Женские", font=('Helvetica', 10, 'bold')).pack()
        
        ttk.Radiobutton(
            female_frame,
            image=self.hair_images["medium"],
            variable=self.hair_style_var,
            value="medium"
        ).pack(pady=5)
        
        ttk.Radiobutton(
            female_frame,
            image=self.hair_images["long_curly"],
            variable=self.hair_style_var,
            value="long_curly"
        ).pack(pady=5)
        
        ttk.Radiobutton(
            female_frame,
            image=self.hair_images["long_straight"],
            variable=self.hair_style_var,
            value="long_straight"
        ).pack(pady=5)
        
        # Цвет волос
        frame = ttk.LabelFrame(parent, text="Цвет волос", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.hair_color_var = tk.StringVar(value="blonde")
        
        color_frame = ttk.Frame(frame)
        color_frame.pack()
        
        for i, (name, color) in enumerate(self.hair_colors.items()):
            if i % 2 == 0:
                row_frame = ttk.Frame(color_frame)
                row_frame.pack(anchor=tk.W)
            
            frame_color = ttk.Frame(row_frame)
            frame_color.pack(side=tk.LEFT, padx=5, pady=2)
            
            color_img = self.create_color_circle(color)
            label = ttk.Label(frame_color, image=color_img)
            label.image = color_img
            label.pack(side=tk.LEFT)
            
            ttk.Radiobutton(
                frame_color,
                text=name.capitalize(),
                variable=self.hair_color_var,
                value=name
            ).pack(side=tk.LEFT, padx=5)
    
    def setup_eyes_selection(self, parent):
        """Выбор формы глаз с изображениями"""
        # Форма глаз
        frame = ttk.LabelFrame(parent, text="Форма глаз", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.eyes_var = tk.StringVar(value="round")
        
        eyes_frame = ttk.Frame(frame)
        eyes_frame.pack()
        
        ttk.Radiobutton(
            eyes_frame,
            image=self.eyes_images["round"],
            variable=self.eyes_var,
            value="round"
        ).pack(side=tk.LEFT, padx=20)
        
        ttk.Radiobutton(
            eyes_frame,
            image=self.eyes_images["almond"],
            variable=self.eyes_var,
            value="almond"
        ).pack(side=tk.LEFT, padx=20)
        
        # Цвет глаз
        frame = ttk.LabelFrame(parent, text="Цвет глаз", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.eyes_color_var = tk.StringVar(value="blue")
        
        color_frame = ttk.Frame(frame)
        color_frame.pack()
        
        for name, color in self.eye_colors.items():
            frame_color = ttk.Frame(color_frame)
            frame_color.pack(side=tk.LEFT, padx=10)
            
            color_img = self.create_color_circle(color)
            label = ttk.Label(frame_color, image=color_img)
            label.image = color_img
            label.pack(side=tk.LEFT)
            
            ttk.Radiobutton(
                frame_color,
                text=name.capitalize(),
                variable=self.eyes_color_var,
                value=name
            ).pack(side=tk.LEFT, padx=5)
    
    def setup_pose_selection(self, parent):
        """Выбор позы персонажа (по пояс/в полный рост)"""
        frame = ttk.LabelFrame(parent, text="Поза персонажа", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.pose_var = tk.StringVar(value="half")
        
        ttk.Radiobutton(
            frame,
            text="По пояс",
            variable=self.pose_var,
            value="half"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            frame,
            text="В полный рост",
            variable=self.pose_var,
            value="full"
        ).pack(anchor=tk.W, pady=2)
    
    def setup_profession_selection(self, parent):
        """Выбор профессии"""
        frame = ttk.LabelFrame(parent, text="Профессия", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        self.profession_var = tk.StringVar(value="control_engineer")
        
        for key, prof in self.professions.items():
            ttk.Radiobutton(
                frame,
                text=prof["name"],
                variable=self.profession_var,
                value=key
            ).pack(anchor=tk.W, pady=2)
    
    # def setup_style_selection(self, parent):
    #     """Выбор стиля рисования"""
    #     frame = ttk.LabelFrame(parent, text="Стиль рисования", padding=10)
    #     frame.pack(fill=tk.X, pady=5)
        
    #     self.style_var = tk.StringVar(value="realistic")
        
    #     styles = [
    #         ("Реалистичный", "realistic"),
    #         ("Аниме", "anime"),
    #         ("3D", "3d")
    #     ]
        
    #     for text, value in styles:
    #         ttk.Radiobutton(
    #             frame,
    #             text=text,
    #             variable=self.style_var,
    #             value=value
    #         ).pack(anchor=tk.W, pady=2)
    
    def start_generation_thread(self):
        """Запуск генерации в отдельном потоке"""
        self.progress.pack(pady=10)
        self.progress.start(10)
        self.generate_btn.config(state=tk.DISABLED)
        self.preview_label.config(image='', text="Генерация изображения...")
        
        thread = threading.Thread(target=self._generate_in_thread, daemon=True)
        thread.start()
    
    def _generate_in_thread(self):
        """Метод для выполнения в отдельном потоке"""
        try:
            prompt = self.build_prompt()
            image_data = self.generate_character_image(prompt)
            
            if image_data:
                self.root.after(0, self.display_generated_image, image_data)
        
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Ошибка", str(e))
        
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)
            self.root.after(0, self.generate_btn.config, {'state': tk.NORMAL})
    
    def build_prompt(self):
        """Сборка промта для генерации с учетом всех параметров"""
        gender = "мужчины" if self.gender_var.get() == "male" else "женщины"
        
        hair_style_map = {
            "side_part": "короткая стрижка с боковым пробором",
            "bob": "мужская стрижка боб",
            "medium": "средняя длина волос",
            "long_curly": "длинные кудрявые волосы",
            "long_straight": "длинные прямые волосы"
        }
        hair_style = hair_style_map[self.hair_style_var.get()]
        
        hair_color_map = {
            "blonde": "светлые",
            "light_brown": "русые",
            "brown": "каштановые",
            "red": "рыжие"
        }
        hair_color = hair_color_map[self.hair_color_var.get()]
        
        eyes_map = {
            "round": "круглые глаза",
            "almond": "узкие глаза"
        }
        eyes = eyes_map[self.eyes_var.get()]
        
        eyes_color_map = {
            "blue": "голубые",
            "green": "зеленые",
            "brown": "карие"
        }
        eyes_color = eyes_color_map[self.eyes_color_var.get()]
        
        skin_color_map = {
            "light": "светлая кожа",
            "medium": "средний цвет кожи",
            "dark": "темная кожа"
        }
        skin_color = skin_color_map[self.skin_color_var.get()]
        
        # Получаем фон для выбранной профессии
        profession_bg = self.professions[self.profession_var.get()]["background"]
        
        pose_map = {
            "half": "по пояс",
            "full": "в полный рост"
        }
        pose = pose_map[self.pose_var.get()]
        
        # style_map = {
        #     "realistic": "реалистичный стиль",
        #     "anime": "аниме стиль",
        #     "3d": "3D стиль"
        # }
        # style = style_map[self.style_var.get()]
        
        return (
            f"Изображение {gender} {pose}, {skin_color}, {hair_style}, {hair_color} волосы, {eyes}, {eyes_color} глаза, "
            f" {profession_bg}, изображение в стиле аниме,реалистично, высокое качество, детализированное изображение, "
            f"хорошо виден фон, Человек смотрит в камеру"
        )
    
    # def display_generated_image(self, image_base64):
    #     """Отображение сгенерированного изображения"""
    #     try:
    #         image_data = base64.b64decode(image_base64)
    #         image = Image.open(io.BytesIO(image_data))
    #         image.thumbnail((500, 500))
    #         photo = ImageTk.PhotoImage(image)
            
    #         self.preview_label.config(image=photo, text="")
    #         self.preview_label.image = photo
            
    #     except Exception as e:
    #         messagebox.showerror("Ошибка", f"Не удалось отобразить изображение: {str(e)}")
    #         self.preview_label.config(image=self.default_preview, text="Ошибка загрузки изображения")

    def display_generated_image(self, image_base64):
        """Отображение сгенерированного изображения"""
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Применяем thumbnail
            image.thumbnail((500, 500))
            
            # Наложение логотипа
            try:
                logo = Image.open(self.logo_path).convert("RGBA")
                logo = logo.resize(self.logo_size)
                
                # Рассчитываем позицию
                position = (
                    image.width - logo.width - 10,  # 10px отступ
                    image.height - logo.height - 10
                )
                
                # Создаем копию изображения для редактирования
                image = image.convert("RGBA")
                image.paste(logo, position, logo)
                image = image.convert("RGB")  # Конвертируем обратно для совместимости
                
            except Exception as logo_error:
                print(f"Ошибка логотипа: {logo_error}")

            # Создаем PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отобразить изображение: {str(e)}")
            self.preview_label.config(image=self.default_preview, text="Ошибка загрузки изображения")

if __name__ == "__main__":
    root = tk.Tk()
    app = CharacterCreatorApp(root)
    root.mainloop()