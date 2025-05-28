import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import io
import base64
import threading
import os
import tempfile
import win32api
import win32print
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
            "profession": tk.StringVar(value=self.model.current_character["profession"]),
            "accessories_glasses": tk.StringVar(value=self.model.current_character["accessories"]["glasses"]),
            "accessories_headwear": tk.StringVar(value=self.model.current_character["accessories"]["headwear"]),
            "accessories_facial": tk.StringVar(value=self.model.current_character["accessories"]["facial"])
        }
        self.current_image = None  # Добавляем атрибут для хранения текущего изображения
        
        # Привязка всех переменных к обработчику
        for param, var in self.ui_vars.items():
            if param.startswith("accessories_"):
                category = param.split("_")[1]
                var.trace_add("write", lambda *args, c=category: self.update_accessory(c))
            else:
                var.trace_add("write", lambda *args, p=param: self.update_parameter(p))
        
        # Загрузка ресурсов
        self.load_images()
        self.setup_styles()
        self.setup_ui()
        self.root.geometry("{0}x{1}+0+0".format(
            self.root.winfo_screenwidth(), 
            self.root.winfo_screenheight()
        ))
        self.root.state('zoomed')  # Развернуть на весь экран
        
    def update_accessory(self, category):
        value = self.ui_vars[f"accessories_{category}"].get()
        self.model.update_accessory(category, value)
        

    def update_parameter(self, parameter: str):
        value = self.ui_vars[parameter].get()
        self.model.update_parameter(parameter, value)
        print(f"Parameter updated: {parameter} = {value}")  # Отладочный вывод
        print("Current character:", self.model.current_character)  # Полное состояние

    def load_images(self):
        """Загрузка изображений для элементов интерфейса"""
        # self.hair_images = {
        #     "side_part": ImageUtils.load_image("assets/hair_short.png", (100, 100)),
        #     "bob": ImageUtils.load_image("assets/hair_bob.png", (100, 100)),
        #     "medium": ImageUtils.load_image("assets/hair_medium.png", (100, 100)),
        #     "long_curly": ImageUtils.load_image("assets/hair_long_curly.png", (100, 100)),
        #     "long_straight": ImageUtils.load_image("assets/hair_long_straight.png", (100, 100))
        # }
        self.hair_images = {
            "side_part": ImageUtils.load_image("assets/hair_short.png", (80, 80)),
            "bob": ImageUtils.load_image("assets/hair_bob.png", (80, 80)),
            "supershort_men's_hair": ImageUtils.load_image("assets/supershort_men's_hair.png", (80, 80)),
            "smalllong_men's_hair": ImageUtils.load_image("assets/smalllong_men's_hair.png", (80, 80)),
            "men's_braids": ImageUtils.load_image("assets/men's_braids.png", (80, 80)),
            "bald": ImageUtils.load_image("assets/bald.png", (80, 80)),
            "medium": ImageUtils.load_image("assets/hair_medium.png", (60, 80)),
            "long_curly": ImageUtils.load_image("assets/hair_long_curly.png", (80, 80)),
            "long_straight": ImageUtils.load_image("assets/hair_long_straight.png", (80, 80)),
            "afro": ImageUtils.load_image("assets/afro.png", (80, 80)),
            "braids": ImageUtils.load_image("assets/braids.png", (80, 90)),
            "two_tail": ImageUtils.load_image("assets/two_tail.png", (80, 80)),
            "long_tail": ImageUtils.load_image("assets/long_tail.png", (80, 80)),
            # "fringe": ImageUtils.load_image("assets/fringe.png", (80, 80)),
            "bunch": ImageUtils.load_image("assets/bunch.png", (80, 80)),
            "piksi": ImageUtils.load_image("assets/piksi.png", (80, 80)),

        }

        
        self.eyes_images = {
            "round": ImageUtils.load_image("assets/eyes_round.png", (80, 40)),
            "almond": ImageUtils.load_image("assets/eyes_almond.png", (80, 30))
        }

        self.accessories_images = {
            "oval_glasses": ImageUtils.load_image("assets/oval_glasses.png", (80, 80)),
            "basic_glasses": ImageUtils.load_image("assets/basic_glasses.png", (80, 80)),
            "circle_glasses": ImageUtils.load_image("assets/circle_glasses.png", (80, 80)),
            "rect_glasses": ImageUtils.load_image("assets/rect_glasses.png", (80, 80)),
            "cap": ImageUtils.load_image("assets/cap.png", (80, 80)),
            "bonnet": ImageUtils.load_image("assets/bonnet.png", (80, 80)),
            "hat": ImageUtils.load_image("assets/hat.png", (80, 80)),
            "beret": ImageUtils.load_image("assets/beret.png", (80, 80)),
            "beard": ImageUtils.load_image("assets/beard.png", (80, 80)),
            "moustache": ImageUtils.load_image("assets/moutstache.png", (80, 80)),
            "sport":ImageUtils.load_image("assets/sports_headband.png", (80, 80)),
        }
        
        self.default_preview = ImageUtils.load_image("assets/logo.png", (400, 400))

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
        
        # Левая панель с настройками (40% ширины)
        left_container = ttk.Frame(main_frame, width=int(self.root.winfo_screenwidth()*0.6))
        left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.setup_left_panel(left_container)
        
        # Правая панель с превью (60% ширины)
        right_container = ttk.Frame(main_frame)
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.setup_right_panel(right_container)

    def setup_left_panel(self, parent):
        """Панель параметров с прокруткой"""
        # Основной контейнер с прокруткой
        container = ttk.Frame(parent)
        container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Создаем Canvas и Scrollbar
        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        # Фрейм для содержимого внутри Canvas
        scroll_frame = ttk.Frame(canvas)
        
        # Привязка прокрутки
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all"),
                width=e.width  # Фиксируем ширину равной содержимому
            )
        )
        
        # Создаем окно для содержимого
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Упаковка элементов
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Обработчик колеса мыши
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Привязка событий мыши
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Добавляем элементы управления
        self.setup_gender_selection(scroll_frame)
        self.setup_skin_color_selection(scroll_frame)
        self.setup_hair_selection(scroll_frame)
        self.setup_eyes_selection(scroll_frame)
        self.setup_accessories_selection(scroll_frame) 
        self.setup_pose_selection(scroll_frame)
        self.setup_profession_selection(scroll_frame)

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
            # text="Здесь будет изображение",
            compound="center",
            font=("Helvetica", 14),
            anchor='center'
        )
        self.preview_label.pack(pady=20, fill=tk.BOTH, expand=True)

        self.print_btn = ttk.Button(
            right_frame,
            text="Печать",
            command=self.print_image,
            state=tk.DISABLED,
            style='Accent.TButton'
        )
        self.print_btn.pack(pady=10, side=tk.BOTTOM)

        
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

    # def setup_skin_color_selection(self, parent):
    #     frame = ttk.LabelFrame(parent, text="Цвет кожи", padding=10)
    #     frame.pack(fill=tk.X, pady=5)
        
    #     color_frame = ttk.Frame(frame)
    #     color_frame.pack()
        
    #     for color_name in COLOR_PALETTE["skin_colors"]:
    #         btn_frame = ttk.Frame(color_frame)
    #         btn_frame.pack(side=tk.LEFT, padx=5)
            
    #         color_img = ImageUtils.create_color_circle(
    #             COLOR_PALETTE["skin_colors"][color_name], 
    #             40
    #         )
    #         ttk.Label(btn_frame, image=color_img).pack()
    #         ttk.Radiobutton(
    #             btn_frame,
    #             text=color_name.capitalize(),
    #             variable=self.ui_vars["skin_color"],
    #             value=color_name
    #         ).pack()
    def setup_skin_color_selection(self, parent):
        frame = ttk.LabelFrame(parent, text="Цвет кожи", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        color_frame = ttk.Frame(frame)
        color_frame.pack()
        
        for color_name in COLOR_PALETTE["skin_colors"]:
            btn_frame = ttk.Frame(color_frame)
            btn_frame.pack(side=tk.LEFT, padx=5)
            
            # Создаем цветной кружок
            color_img = ImageUtils.create_color_circle(
                COLOR_PALETTE["skin_colors"][color_name], 
                40
            )
            
            # Упаковываем только кружок без текста
            ttk.Radiobutton(
                btn_frame,
                image=color_img,
                variable=self.ui_vars["skin_color"],
                value=color_name
            ).pack()
            
            # Сохраняем ссылку на изображение
            btn_frame.image = color_img

    # def setup_hair_selection(self, parent):
    #     # Выбор стиля прически
    #     frame = ttk.LabelFrame(parent, text="Прическа", padding=10)
    #     frame.pack(fill=tk.X, pady=5)
        
    #     hair_grid = ttk.Frame(frame)
    #     hair_grid.pack()
        
    #     # Мужские прически
    #     male_frame = ttk.Frame(hair_grid)
    #     male_frame.pack(side=tk.LEFT, padx=10)
    #     ttk.Label(male_frame, text="Мужские", font=('Helvetica', 10, 'bold')).pack()
        
    #     for style in ["side_part", "bob"]:
    #         ttk.Radiobutton(
    #             male_frame,
    #             image=self.hair_images[style],
    #             variable=self.ui_vars["hair_style"],
    #             value=style
    #         ).pack(pady=5)
        
    #     # Женские прически
    #     female_frame = ttk.Frame(hair_grid)
    #     female_frame.pack(side=tk.LEFT, padx=10)
    #     ttk.Label(female_frame, text="Женские", font=('Helvetica', 10, 'bold')).pack()
        
    #     for style in ["medium", "long_curly", "long_straight"]:
    #         ttk.Radiobutton(
    #             female_frame,
    #             image=self.hair_images[style],
    #             variable=self.ui_vars["hair_style"],
    #             value=style
    #         ).pack(pady=5)
        
    #     # Выбор цвета волос
    #     frame = ttk.LabelFrame(parent, text="Цвет волос", padding=10)
    #     frame.pack(fill=tk.X, pady=5)
        
    #     color_frame = ttk.Frame(frame)
    #     color_frame.pack()
        
    #     for color_name in COLOR_PALETTE["hair_colors"]:
    #         btn_frame = ttk.Frame(color_frame)
    #         btn_frame.pack(side=tk.LEFT, padx=5)
            
    #         color_img = ImageUtils.create_color_circle(
    #             COLOR_PALETTE["hair_colors"][color_name], 
    #             30
    #         )
    #         ttk.Label(btn_frame, image=color_img).pack()
    #         ttk.Radiobutton(
    #             btn_frame,
    #             text=color_name.capitalize(),
    #             variable=self.ui_vars["hair_color"],
    #             value=color_name
    #         ).pack()
    def setup_hair_selection(self, parent):
        # Выбор стиля прически
        frame = ttk.LabelFrame(parent, text="Прическа", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        # Создаем фрейм для сетки причесок
        hair_grid = ttk.Frame(frame)
        hair_grid.pack()
        
        # Все доступные прически
        all_hair_styles = [
            "side_part", "bob", "supershort_men's_hair",
            "smalllong_men's_hair", "men's_braids", "bald",
            "medium", "long_curly", "long_straight", "afro",
            "braids", "two_tail", "long_tail", #"fringe", 
            "bunch", "piksi"
        ]
        
        # Отображаем прически в сетке 4 колонки
        for i, style in enumerate(all_hair_styles):
            if i % 4 == 0:  # Новая строка после каждых 4 причесок
                row_frame = ttk.Frame(hair_grid)
                row_frame.pack(fill=tk.X)
            
            hair_container = ttk.Frame(row_frame, padding=5)
            hair_container.pack(side=tk.LEFT, padx=5)
            
            # Изображение прически
            ttk.Label(
                hair_container, 
                image=self.hair_images[style]
            ).pack()
            
            # Название прически
            tk.Radiobutton(
                hair_container,
                text=style.replace("_", " ").replace("'s", "").capitalize(),
                variable=self.ui_vars["hair_style"],
                value=style,
                wraplength=100,
                background="white",
                font=("Helvetica", 9)
            ).pack()
        
        # Выбор цвета волос
        color_frame = ttk.LabelFrame(parent, text="Цвет волос", padding=10)
        color_frame.pack(fill=tk.X, pady=5)
        
        color_grid = ttk.Frame(color_frame)
        color_grid.pack()
        
        for color_name in COLOR_PALETTE["hair_colors"]:
            btn_frame = ttk.Frame(color_grid)
            btn_frame.pack(side=tk.LEFT, padx=5)
            
            # Создаем цветной кружок
            color_img = ImageUtils.create_color_circle(
                COLOR_PALETTE["hair_colors"][color_name], 
                30
            )
            
            # Упаковываем только кружок без текста
            ttk.Radiobutton(
                btn_frame,
                image=color_img,
                variable=self.ui_vars["hair_color"],
                value=color_name
            ).pack()
            
            # Сохраняем ссылку на изображение
            btn_frame.image = color_img
        

    # def setup_eyes_selection(self, parent):
    #     """Выбор формы и цвета глаз"""
    #     # Форма глаз
    #     frame = ttk.LabelFrame(parent, text="Форма глаз", padding=10)
    #     frame.pack(fill=tk.X, pady=5)
        
    #     eyes_frame = ttk.Frame(frame)
    #     eyes_frame.pack()
        
    #     ttk.Radiobutton(
    #         eyes_frame,
    #         image=self.eyes_images["round"],
    #         variable=self.ui_vars["eyes"],
    #         value="round"
    #     ).pack(side=tk.LEFT, padx=20)
        
    #     ttk.Radiobutton(
    #         eyes_frame,
    #         image=self.eyes_images["almond"],
    #         variable=self.ui_vars["eyes"],
    #         value="almond"
    #     ).pack(side=tk.LEFT, padx=20)
        
    #     # Цвет глаз
    #     frame = ttk.LabelFrame(parent, text="Цвет глаз", padding=10)
    #     frame.pack(fill=tk.X, pady=5)
        
    #     color_frame = ttk.Frame(frame)
    #     color_frame.pack()
        
    #     for color_name in COLOR_PALETTE["eye_colors"]:
    #         btn_frame = ttk.Frame(color_frame)
    #         btn_frame.pack(side=tk.LEFT, padx=5)
            
    #         color_img = ImageUtils.create_color_circle(
    #             COLOR_PALETTE["eye_colors"][color_name], 
    #             30
    #         )
    #         ttk.Label(btn_frame, image=color_img).pack()
    #         ttk.Radiobutton(
    #             btn_frame,
    #             text=color_name.capitalize(),
    #             variable=self.ui_vars["eyes_color"],
    #             value=color_name
    #         ).pack()
    def setup_eyes_selection(self, parent):
        """Выбор формы и цвета глаз"""
        # Форма глаз (оставляем как было)
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
        
        # Цвет глаз (обновляем для кружков)
        frame = ttk.LabelFrame(parent, text="Цвет глаз", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        color_frame = ttk.Frame(frame)
        color_frame.pack()
        
        for color_name in COLOR_PALETTE["eye_colors"]:
            btn_frame = ttk.Frame(color_frame)
            btn_frame.pack(side=tk.LEFT, padx=5)
            
            # Создаем цветной кружок
            color_img = ImageUtils.create_color_circle(
                COLOR_PALETTE["eye_colors"][color_name], 
                30
            )
            
            # Упаковываем только кружок без текста
            ttk.Radiobutton(
                btn_frame,
                image=color_img,
                variable=self.ui_vars["eyes_color"],
                value=color_name
            ).pack()
            
            # Сохраняем ссылку на изображение
            btn_frame.image = color_img
    def setup_accessories_selection(self, parent):
        """Выбор аксессуаров по категориям"""
        frame = ttk.LabelFrame(parent, text="Аксессуары", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка для очков
        glasses_frame = ttk.Frame(notebook)
        notebook.add(glasses_frame, text="Очки")
        self._setup_accessory_category(glasses_frame, "glasses")
        
        # Вкладка для головных уборов
        headwear_frame = ttk.Frame(notebook)
        notebook.add(headwear_frame, text="Головные уборы")
        self._setup_accessory_category(headwear_frame, "headwear")
        
        # Вкладка для лицевых аксессуаров
        facial_frame = ttk.Frame(notebook)
        notebook.add(facial_frame, text="Лицевые")
        self._setup_accessory_category(facial_frame, "facial")

    def _setup_accessory_category(self, parent, category):
        """Настройка выбора для одной категории аксессуаров"""
        category_names = {
            "glasses": "Очки",
            "headwear": "Головной убор",
            "facial": "Лицевые"
        }
        
        frame = ttk.LabelFrame(parent, text=category_names[category], padding=5)
        frame.pack(fill=tk.X, pady=5)
        
        grid_frame = ttk.Frame(frame)
        grid_frame.pack(fill=tk.X)
        
        row_frame = None
        for i, accessory in enumerate(self.model.accessories_categories[category]):
            if i % 4 == 0:
                row_frame = ttk.Frame(grid_frame)
                row_frame.pack(fill=tk.X)
            
            container = ttk.Frame(row_frame, padding=5)
            container.pack(side=tk.LEFT)
            
            if accessory != "none":
                ttk.Label(
                    container,
                    image=self.accessories_images[accessory]
                ).pack()
            
            text = "Нет" if accessory == "none" else self.model._get_accessory_name(accessory)
            ttk.Radiobutton(
                container,
                text=text,
                variable=self.ui_vars[f"accessories_{category}"],
                value=accessory
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
            self.preview_label.config(text="")
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
            self.current_image = image  # Сохраняем изображение
            self.print_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            self.preview_label.config(image=self.default_preview, text="Ошибка загрузки")
            messagebox.showerror("Ошибка", f"Не удалось отобразить изображение: {str(e)}")

    def print_image(self):
        """Печать изображения на принтере по умолчанию"""
        if not self.current_image:
            messagebox.showerror("Ошибка", "Нет изображения для печати")
            return

        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as tmp:
                self.current_image.save(tmp.name, "BMP")
                
                # Получаем дескриптор принтера по умолчанию
                printer_name = win32print.GetDefaultPrinter()
                hprinter = win32print.OpenPrinter(printer_name)
                
                try:
                    # Начинаем задание на печать
                    win32print.StartDocPrinter(hprinter, 1, ("Python Print", None, "RAW"))
                    win32print.StartPagePrinter(hprinter)
                    
                    # Отправляем данные на печать
                    with open(tmp.name, "rb") as f:
                        data = f.read()
                    win32api.ShellExecute(0, "print", tmp.name, None, ".", 0)
                    
                    # Завершаем печать
                    win32print.EndPagePrinter(hprinter)
                    win32print.EndDocPrinter(hprinter)
                    
                finally:
                    win32print.ClosePrinter(hprinter)
                
        except Exception as e:
            messagebox.showerror("Ошибка печати", f"Не удалось распечатать изображение:\n{str(e)}")