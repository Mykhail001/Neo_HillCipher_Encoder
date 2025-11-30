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

        # Track open windows
        self.alphabet_window = None
        self.substitution_window = None
        self.matrix_window = None
        self.encrypt_window = None
        self.decrypt_window = None
        self.brute_force_window = None

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
        if self.alphabet_window is not None and self.alphabet_window.window.winfo_exists():
            self.alphabet_window.window.focus()
            return
        from ui.alphabet_window import AlphabetWindow
        self.alphabet_window = AlphabetWindow(self.root)

    def open_substitution_window(self):
        """Відкрити вікно створення підстановки"""
        if self.substitution_window is not None and self.substitution_window.window.winfo_exists():
            self.substitution_window.window.focus()
            return
        from ui.substitution_window import SubstitutionWindow
        self.substitution_window = SubstitutionWindow(self.root)

    def open_matrix_window(self):
        """Відкрити вікно створення матриці"""
        if self.matrix_window is not None and self.matrix_window.window.winfo_exists():
            self.matrix_window.window.focus()
            return
        from ui.matrix_window import MatrixWindow
        self.matrix_window = MatrixWindow(self.root)

    def open_encrypt_window(self):
        """Відкрити вікно шифрування"""
        if self.encrypt_window is not None and self.encrypt_window.window.winfo_exists():
            self.encrypt_window.window.focus()
            return
        from ui.encrypt_window import EncryptWindow
        self.encrypt_window = EncryptWindow(self.root)

    def open_decrypt_window(self):
        """Відкрити вікно розшифрування"""
        if self.decrypt_window is not None and self.decrypt_window.window.winfo_exists():
            self.decrypt_window.window.focus()
            return
        from ui.decrypt_window import DecryptWindow
        self.decrypt_window = DecryptWindow(self.root)

    def open_brute_force_window(self):
        """Відкрити вікно брутфорсу"""
        if self.brute_force_window is not None and self.brute_force_window.window.winfo_exists():
            self.brute_force_window.window.focus()
            return
        from ui.brute_force_window import BruteForceWindow
        self.brute_force_window = BruteForceWindow(self.root)

    def run(self):
        """Запуск головного циклу"""
        self.root.mainloop()