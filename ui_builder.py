import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import io
import base64
import threading
import os
from config import API_CONFIG, PROFESSIONS, COLOR_PALETTE
from character_model import CharacterModel
from api_handler import ApiHandler
from utils import ImageUtils


class CharacterCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конструктор будущего инженера")
        self.root.geometry("1200x800")
        
        # Инициализация компонентов
        self.model = CharacterModel()
        self.api = ApiHandler()
        self.image_utils = ImageUtils()
        self.ui_vars = {
            "gender": tk.StringVar(value=self.model.current_character["gender"]),
            "hair_style": tk.StringVar(value=self.model.current_character["hair_style"]),
            "hair_color": tk.StringVar(value=self.model.current_character["hair_color"]),
            "eyes": tk.StringVar(value=self.model.current_character["eyes"]),
            "eyes_color": tk.StringVar(value=self.model.current_character["eyes_color"]),
            "skin_color": tk.StringVar(value=self.model.current_character["skin_color"]),
            "pose": tk.StringVar(value=self.model.current_character["pose"]),
            "profession": tk.StringVar(value=self.model.current_character["profession"])
        }
        
        # Привязка всех переменных к обработчику
        for param, var in self.ui_vars.items():
            var.trace_add("write", lambda *args, p=param: self.update_parameter(p))
        
        # Загрузка ресурсов
        self.load_images()
        self.setup_styles()
        self.setup_ui()

        

    def update_parameter(self, parameter: str):
        value = self.ui_vars[parameter].get()
        self.model.update_parameter(parameter, value)
        print(f"Parameter updated: {parameter} = {value}")  # Отладочный вывод
        print("Current character:", self.model.current_character)  # Полное состояние

    def load_images(self):
        """Загрузка изображений для элементов интерфейса"""
        self.hair_images = {
            "side_part": ImageUtils.load_image("assets/hair_short.png", (100, 100)),
            "bob": ImageUtils.load_image("assets/hair_bob.png", (100, 100)),
            "medium": ImageUtils.load_image("assets/hair_medium.png", (100, 100)),
            "long_curly": ImageUtils.load_image("assets/hair_long_curly.png", (100, 100)),
            "long_straight": ImageUtils.load_image("assets/hair_long_straight.png", (100, 100))
        }
        
        self.eyes_images = {
            "round": ImageUtils.load_image("assets/eyes_round.png", (80, 40)),
            "almond": ImageUtils.load_image("assets/eyes_almond.png", (80, 30))
        }
        
        self.default_preview = ImageUtils.create_sample_image("default", (400, 400), "#EEEEEE")

    def setup_styles(self):
        """Настройка стилей интерфейса"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Основные стили
        style.configure("TFrame", background="#FFFFFF")
        style.configure("TLabel", background="#FFFFFF", font=("Helvetica", 11))
        style.configure("TLabelframe", background="#FFFFFF", borderwidth=2, relief="groove")
        style.configure("TLabelframe.Label", background="#FFFFFF", foreground="#0F45C7", 
                       font=("Helvetica", 12, "bold"))
        
        # Стиль кнопки генерации
        style.configure("Accent.TButton",
                        background="#F04D23",
                        foreground="#FFFFFF",
                        font=("Helvetica", 12, "bold"),
                        padding=10)
        style.map("Accent.TButton",
                background=[("active", "#d9441e")],
                relief=[("pressed", "groove")])
        
        # Стиль прогресс-бара
        style.configure("Horizontal.TProgressbar",
                        background="#F04D23",
                        troughcolor="#FFFFFF",
                        bordercolor="#FFFFFF",
                        thickness=10)

    def setup_ui(self):
        """Основная настройка интерфейса"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель с настройками
        self.setup_left_panel(main_frame)
        
        # Правая панель с превью
        self.setup_right_panel(main_frame)

    def setup_left_panel(self, parent):
        """Панель параметров с прокруткой"""
        container = ttk.Frame(parent)
        container.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Элементы управления
        self.setup_gender_selection(scroll_frame)
        self.setup_skin_color_selection(scroll_frame)
        self.setup_hair_selection(scroll_frame)
        self.setup_eyes_selection(scroll_frame)
        self.setup_pose_selection(scroll_frame)
        self.setup_profession_selection(scroll_frame)

        # ====== СТИЛИЗАЦИЯ В СТИЛЕ МИЭТа ======
        self.root.configure(bg="#FFFFFF")
        # Настройка стиля
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Lab Grotesque', 12, 'bold'))
        
        style.theme_use("clam")

        style.configure("TFrame", background="#FFFFFF")
        style.configure("TLabel", background="#FFFFFF", font=("Lab Grotesque", 11))
        style.configure("TLabelframe", background="#FFFFFF", borderwidth=2, relief="groove")
        style.configure("TLabelframe.Label", background="#FFFFFF", foreground="#0F45C7", font=("Helvetica", 12, "bold"))
        style.configure("TRadiobutton", background="#FFFFFF", font=("Lab Grotesque", 10), foreground="#000000")
        style.map("TRadiobutton", foreground=[("active", "#0F45C7")])

        # Кнопка генерации (оранжевый МИЭТ)
        style.configure("Accent.TButton",
                        background="#0f45c7",
                        foreground="#FFFFFF",
                        font=("Lab Grotesque", 12, "bold"),
                        padding=10,
                        relief="flat")
        style.map("Accent.TButton",
                background=[("active", "#F04D23")],
                relief=[("pressed", "groove")])

        # Прогресс-бар (оранжевый индикатор на белом фоне)
        style.configure("TProgressbar",
                        background="#F04D23",
                        troughcolor="#FFFFFF",
                        bordercolor="#FFFFFF",
                        lightcolor="#F04D23",
                        darkcolor="#F04D23")

    def setup_right_panel(self, parent):
        """Панель превью и управления генерацией"""
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Кнопка генерации
        self.generate_btn = ttk.Button(
            right_frame,
            text="Сгенерировать персонажа",
            style="Accent.TButton",
            command=self.start_generation_thread
        )
        self.generate_btn.pack(pady=20, ipadx=20, ipady=10)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(
            right_frame,
            orient="horizontal",
            mode="indeterminate",
            style="Horizontal.TProgressbar",
            length=400
        )
        
        # Область превью
        self.preview_label = ttk.Label(
            right_frame,
            image=self.default_preview,
            text="Здесь будет изображение",
            compound="center",
            font=("Helvetica", 14),
            anchor='center'
        )
        self.preview_label.pack(pady=20, fill=tk.BOTH, expand=True)

    # Методы настройки элементов управления
        
    def setup_gender_selection(self, parent):
        frame = ttk.LabelFrame(parent, text="Пол", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(
            frame,
            text="Мужской",
            variable=self.ui_vars["gender"],
            value="male"
        ).pack(side=tk.LEFT, padx=20)
        
        ttk.Radiobutton(
            frame,
            text="Женский",
            variable=self.ui_vars["gender"],
            value="female"
        ).pack(side=tk.LEFT, padx=20)

    def setup_skin_color_selection(self, parent):
        frame = ttk.LabelFrame(parent, text="Цвет кожи", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        color_frame = ttk.Frame(frame)
        color_frame.pack()
        
        for color_name in COLOR_PALETTE["skin_colors"]:
            btn_frame = ttk.Frame(color_frame)
            btn_frame.pack(side=tk.LEFT, padx=5)
            
            color_img = ImageUtils.create_color_circle(
                COLOR_PALETTE["skin_colors"][color_name], 
                40
            )
            ttk.Label(btn_frame, image=color_img).pack()
            ttk.Radiobutton(
                btn_frame,
                text=color_name.capitalize(),
                variable=self.ui_vars["skin_color"],
                value=color_name
            ).pack()

    def setup_hair_selection(self, parent):
        # Выбор стиля прически
        frame = ttk.LabelFrame(parent, text="Прическа", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        hair_grid = ttk.Frame(frame)
        hair_grid.pack()
        
        # Мужские прически
        male_frame = ttk.Frame(hair_grid)
        male_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(male_frame, text="Мужские", font=('Helvetica', 10, 'bold')).pack()
        
        for style in ["side_part", "bob"]:
            ttk.Radiobutton(
                male_frame,
                image=self.hair_images[style],
                variable=self.ui_vars["hair_style"],
                value=style
            ).pack(pady=5)
        
        # Женские прически
        female_frame = ttk.Frame(hair_grid)
        female_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(female_frame, text="Женские", font=('Helvetica', 10, 'bold')).pack()
        
        for style in ["medium", "long_curly", "long_straight"]:
            ttk.Radiobutton(
                female_frame,
                image=self.hair_images[style],
                variable=self.ui_vars["hair_style"],
                value=style
            ).pack(pady=5)
        
        # Выбор цвета волос
        frame = ttk.LabelFrame(parent, text="Цвет волос", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        color_frame = ttk.Frame(frame)
        color_frame.pack()
        
        for color_name in COLOR_PALETTE["hair_colors"]:
            btn_frame = ttk.Frame(color_frame)
            btn_frame.pack(side=tk.LEFT, padx=5)
            
            color_img = ImageUtils.create_color_circle(
                COLOR_PALETTE["hair_colors"][color_name], 
                30
            )
            ttk.Label(btn_frame, image=color_img).pack()
            ttk.Radiobutton(
                btn_frame,
                text=color_name.capitalize(),
                variable=self.ui_vars["hair_color"],
                value=color_name
            ).pack()
    
    def setup_eyes_selection(self, parent):
        """Выбор формы и цвета глаз"""
        # Форма глаз
        frame = ttk.LabelFrame(parent, text="Форма глаз", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        eyes_frame = ttk.Frame(frame)
        eyes_frame.pack()
        
        ttk.Radiobutton(
            eyes_frame,
            image=self.eyes_images["round"],
            variable=self.ui_vars["eyes"],
            value="round"
        ).pack(side=tk.LEFT, padx=20)
        
        ttk.Radiobutton(
            eyes_frame,
            image=self.eyes_images["almond"],
            variable=self.ui_vars["eyes"],
            value="almond"
        ).pack(side=tk.LEFT, padx=20)
        
        # Цвет глаз
        frame = ttk.LabelFrame(parent, text="Цвет глаз", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        color_frame = ttk.Frame(frame)
        color_frame.pack()
        
        for color_name in COLOR_PALETTE["eye_colors"]:
            btn_frame = ttk.Frame(color_frame)
            btn_frame.pack(side=tk.LEFT, padx=5)
            
            color_img = ImageUtils.create_color_circle(
                COLOR_PALETTE["eye_colors"][color_name], 
                30
            )
            ttk.Label(btn_frame, image=color_img).pack()
            ttk.Radiobutton(
                btn_frame,
                text=color_name.capitalize(),
                variable=self.ui_vars["eyes_color"],
                value=color_name
            ).pack()

    def setup_pose_selection(self, parent):
        """Выбор позы персонажа"""
        frame = ttk.LabelFrame(parent, text="Поза", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(
            frame,
            text="По пояс",
            variable=self.ui_vars["pose"],
            value="half"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            frame,
            text="В полный рост",
            variable=self.ui_vars["pose"],
            value="full"
        ).pack(anchor=tk.W, pady=2)

    def setup_profession_selection(self, parent):
        """Выбор профессии"""
        frame = ttk.LabelFrame(parent, text="Профессия", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        for prof_id, prof_data in PROFESSIONS.items():
            ttk.Radiobutton(
                frame,
                text=prof_data["name"],
                variable=self.ui_vars["profession"],
                value=prof_id
            ).pack(anchor=tk.W, pady=2)
    def start_generation_thread(self):
        """Запуск генерации в отдельном потоке"""
        self.progress.pack(pady=10)
        self.generate_btn.config(state=tk.DISABLED)
        self.progress.start(10)
        self.preview_label.config(image="", text="Генерация изображения...")
        
        thread = threading.Thread(target=self.generate_image, daemon=True)
        thread.start()

    def generate_image(self):
        """Основная логика генерации изображения"""
        try:
            print(self.model)
            prompt = self.model.build_prompt()
            image_data = self.api.generate_image(prompt)
            self.display_generated_image(image_data)
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Ошибка", str(e))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.generate_btn.config(state=tk.NORMAL))

    def display_generated_image(self, image_base64):
        """Отображение результата с водяным знаком"""
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail((500, 500))
            
            # Добавление водяного знака
            image = self.image_utils.add_watermark(
                image.convert("RGBA"),
                API_CONFIG["LOGO_PATH"],
                API_CONFIG["LOGO_SIZE"]
            )
            
            photo = ImageTk.PhotoImage(image.convert("RGB"))
            self.preview_label.config(image=photo)
            self.preview_label.image = photo
            
        except Exception as e:
            self.preview_label.config(image=self.default_preview, text="Ошибка загрузки")
            messagebox.showerror("Ошибка", f"Не удалось отобразить изображение: {str(e)}")