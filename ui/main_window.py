"""
Головне вікно програми
"""

import tkinter as tk
from config import *


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hill Cipher MultiTool")
        self.root.geometry("500x450")
        self.root.configure(bg=BG_COLOR)

        self.create_widgets()

    def create_widgets(self):
        """Створення віджетів головного меню"""
        tk.Button(
            self.root,
            text="Створити алфавіт",
            command=self.open_alphabet_window,
            font=FONT_BOLD,
            bg=BUTTON_BG,
            fg=FG_COLOR,
            width=25,
            height=2
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Створити підстановку",
            command=self.open_substitution_window,
            font=FONT_BOLD,
            bg=BUTTON_BG,
            fg=FG_COLOR,
            width=25,
            height=2
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Створити матрицю",
            command=self.open_matrix_window,
            font=FONT_BOLD,
            bg=BUTTON_BG,
            fg=FG_COLOR,
            width=25,
            height=2
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Зашифрувати",
            command=self.open_encrypt_window,
            font=FONT_BOLD,
            bg=BUTTON_BG,
            fg=FG_COLOR,
            width=25,
            height=2
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Розшифрувати",
            command=self.open_decrypt_window,
            font=FONT_BOLD,
            bg=BUTTON_BG,
            fg=FG_COLOR,
            width=25,
            height=2
        ).pack(pady=10)
        """
        tk.Button(
            self.root,
            text="Брутфорс",
            command=self.open_brute_force_window,
            font=FONT_BOLD,
            bg=BUTTON_BG,
            fg=FG_COLOR,
            width=25,
            height=2
        ).pack(pady=10)
        """
    def open_alphabet_window(self):
        """Відкрити вікно створення алфавіту"""
        from ui.alphabet_window import AlphabetWindow
        AlphabetWindow(self.root)

    def open_substitution_window(self):
        """Відкрити вікно створення підстановки"""
        from ui.substitution_window import SubstitutionWindow
        SubstitutionWindow(self.root)

    def open_matrix_window(self):
        """Відкрити вікно створення матриці"""
        from ui.matrix_window import MatrixWindow
        MatrixWindow(self.root)

    def open_encrypt_window(self):
        """Відкрити вікно шифрування"""
        from ui.encrypt_window import EncryptWindow
        EncryptWindow(self.root)

    def open_decrypt_window(self):
        """Відкрити вікно розшифрування"""
        from ui.decrypt_window import DecryptWindow
        DecryptWindow(self.root)

    def open_brute_force_window(self):
        """Відкрити вікно брутфорсу"""
        from ui.brute_force_window import BruteForceWindow
        BruteForceWindow(self.root)

    def run(self):
        """Запуск головного циклу"""
        self.root.mainloop()