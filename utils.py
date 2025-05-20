from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
import os

class ImageUtils:
    @staticmethod
    def load_image(path, size):
        try:
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            return ImageUtils.create_sample_image("Error", size, "#FFCCCC")

    @staticmethod
    def create_sample_image(name, size, color):
        img = Image.new('RGB', size, color=color)
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), name, fill="black")
        return ImageTk.PhotoImage(img)

    @staticmethod
    def create_color_circle(color, size=30):
        img = Image.new('RGB', (size, size), color='white')
        draw = ImageDraw.Draw(img)
        draw.ellipse((2, 2, size-2, size-2), fill=color)
        return ImageTk.PhotoImage(img)

    @staticmethod
    def add_watermark(base_image, logo_path, logo_size):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo = logo.resize(logo_size)
            position = (
                base_image.width - logo.width - 10,
                base_image.height - logo.height - 10
            )
            base_image.paste(logo, position, logo)
            return base_image
        except Exception as e:
            return 'lfllflf'+base_image