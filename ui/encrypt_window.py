"""
Вікно шифрування
"""

import tkinter as tk
from tkinter import messagebox
from config import *
from cipher.hill_cipher import (
    text_to_numbers,
    hill_encrypt_standard,
    hill_encrypt_modified
)
from utils.file_utils import load_text_file, load_matrix_file, save_file
from data.templates import ALPHABET_UKR


class EncryptWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Зашифровувач")
        self.window.state('zoomed')
        self.window.configure(bg=BG_COLOR)

        self.alphabet = ALPHABET_UKR
        self.alphabet_name = "Український"
        self.substitution_mapping = []
        self.loaded_matrix = None

        self.create_widgets()

    def create_widgets(self):
        """Створення всіх віджетів"""
        # Алфавіт
        top_frame = tk.Frame(self.window, bg=BG_COLOR)
        top_frame.pack(pady=5)
        tk.Label(
            top_frame,
            text="Алфавіт:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.alphabet_info_var = tk.StringVar(value=f"{self.alphabet_name} ({len(self.alphabet)})")
        tk.Label(
            top_frame,
            textvariable=self.alphabet_info_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_NORMAL
        ).pack(side="left", padx=5)

        tk.Button(
            top_frame,
            text="Відкрити алфавіт",
            command=self.open_alphabet_file,
            bg=CELL_BG,
            fg="black"
        ).pack(side="left", padx=5)

        # Режим шифрування
        mode_frame = tk.Frame(self.window, bg=BG_COLOR)
        mode_frame.pack(pady=5)
        self.encryption_mode = tk.IntVar(value=0)

        tk.Radiobutton(
            mode_frame,
            text="Стандартне шифрування",
            variable=self.encryption_mode,
            value=0,
            indicatoron=0,
            width=25,
            height=2,
            bg=CELL_BG,
            fg="black",
            selectcolor=ACCENT_COLOR,
            activebackground=BUTTON_BG,
            relief="raised",
            command=self.update_subst_visibility
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            mode_frame,
            text="Модифіковане шифрування",
            variable=self.encryption_mode,
            value=1,
            indicatoron=0,
            width=25,
            height=2,
            bg=CELL_BG,
            fg="black",
            selectcolor=ACCENT_COLOR,
            activebackground=BUTTON_BG,
            relief="raised",
            command=self.update_subst_visibility
        ).pack(side="left", padx=5)

        # Підстановка
        self.subst_frame = tk.Frame(self.window, bg=BG_COLOR)
        tk.Label(
            self.subst_frame,
            text="Підстановка:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.subst_name_var = tk.StringVar(value="Відсутня")
        tk.Label(
            self.subst_frame,
            textvariable=self.subst_name_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_NORMAL
        ).pack(side="left", padx=5)

        tk.Button(
            self.subst_frame,
            text="Вибрати підстановку",
            command=self.load_substitution,
            bg=CELL_BG,
            fg="black"
        ).pack(side="left", padx=5)

        # Довжина шуму
        self.noise_frame = tk.Frame(self.window, bg=BG_COLOR)
        tk.Label(
            self.noise_frame,
            text="Довжина шуму:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.noise_length_entry = tk.Entry(self.noise_frame, width=10, bg=CELL_BG, font=("Arial", 11))
        self.noise_length_entry.insert(0, "0")
        self.noise_length_entry.pack(side="left", padx=5)

        # Текст
        tk.Label(
            self.window,
            text="Текст:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(pady=5)

        self.input_text = tk.Text(self.window, width=60, height=10, state="disabled", bg=CELL_BG, font=("Arial", 11))
        self.input_text.pack(pady=5)

        tk.Button(
            self.window,
            text="Відкрити текстовий файл",
            command=self.load_text,
            bg=CELL_BG,
            fg="black"
        ).pack(pady=5)

        # Матриця
        matrix_label_frame = tk.Frame(self.window, bg=BG_COLOR)
        matrix_label_frame.pack(pady=5)
        tk.Label(
            matrix_label_frame,
            text="Матриця для шифрування:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.loaded_matrix_var = tk.StringVar(value="None")
        tk.Label(
            matrix_label_frame,
            textvariable=self.loaded_matrix_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_NORMAL
        ).pack(side="left", padx=5)

        tk.Button(
            matrix_label_frame,
            text="Завантажити матрицю",
            command=self.load_key_matrix,
            bg=CELL_BG,
            fg="black"
        ).pack(side="left", padx=5)

        # Кнопка шифрування
        self.encrypt_btn = tk.Button(
            self.window,
            text="Зашифрувати текст",
            font=FONT_BOLD,
            bg=BUTTON_BG,
            fg=FG_COLOR,
            command=self.encrypt
        )
        self.encrypt_btn.pack(pady=10)

        self.update_subst_visibility()

    def create_alphabet_cell(self, parent, alphabet_name, alphabet_length):
        """Створення інформаційної клітинки для алфавіту (deprecated)"""
        pass

    def open_alphabet_file(self):
        """Відкрити файл алфавіту"""
        from utils.file_utils import load_alphabet_file

        result = load_alphabet_file()
        if result is None:
            return

        content, name = result
        self.alphabet = content
        self.alphabet_name = name

        self.alphabet_info_var.set(f"{self.alphabet_name} ({len(self.alphabet)})")
        messagebox.showinfo("Інформація", f"Алфавіт завантажено:\n{self.alphabet}")

    def update_subst_visibility(self):
        """Оновити видимість підстановки та шуму"""
        if self.encryption_mode.get() == 1:
            self.subst_frame.pack(pady=5, before=self.encrypt_btn)
            self.noise_frame.pack(pady=5, before=self.encrypt_btn)
        else:
            self.subst_frame.pack_forget()
            self.noise_frame.pack_forget()

    def load_substitution(self):
        """Завантажити підстановку"""
        from utils.file_utils import load_substitution_file

        result = load_substitution_file()
        if result is None:
            return

        mapping, name = result

        if len(mapping) != len(self.alphabet):
            messagebox.showerror(
                "Помилка",
                f"Розмір підстановки ({len(mapping)}) != розмір алфавіту ({len(self.alphabet)})."
            )
            return

        self.substitution_mapping = mapping
        self.subst_name_var.set(name)

    def load_text(self):
        """Завантажити текст"""
        text = load_text_file()
        if text:
            self.input_text.config(state="normal")
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, text)
            self.input_text.config(state="disabled")

    def load_key_matrix(self):
        """Завантажити ключову матрицю"""
        matrix, name = load_matrix_file()
        if matrix is not None:
            self.loaded_matrix = matrix
            self.loaded_matrix_var.set(name if name else "Завантажено")

    def encrypt(self):
        """Зашифрувати текст"""
        if not self.alphabet:
            messagebox.showerror("Помилка", "Алфавіт не завантажено!")
            return
        if self.loaded_matrix is None:
            messagebox.showerror("Помилка", "Завантажте ключову матрицю!")
            return

        self.input_text.config(state="normal")
        txt = self.input_text.get("1.0", tk.END).strip()
        self.input_text.config(state="disabled")

        if not txt:
            messagebox.showerror("Помилка", "Текст порожній!")
            return

        try:
            if self.encryption_mode.get() == 0:
                numbers = text_to_numbers(txt, self.alphabet)
                enc_numbers = hill_encrypt_standard(
                    numbers,
                    self.loaded_matrix,
                    self.alphabet
                )
                enc_txt = "".join(self.alphabet[num] for num in enc_numbers)
            else:
                if not self.substitution_mapping:
                    messagebox.showerror("Помилка", "Підстановку не вибрано!")
                    return
                if len(self.substitution_mapping) != len(self.alphabet):
                    messagebox.showerror(
                        "Помилка",
                        f"Розмір підстановки ({len(self.substitution_mapping)}) != розмір алфавіту ({len(self.alphabet)})."
                    )
                    return

                # Отримати довжину шуму
                noise_str = self.noise_length_entry.get().strip()
                noise_length = int(noise_str) if noise_str else 0

                if noise_length < 0:
                    messagebox.showerror("Помилка", "Довжина шуму має бути >= 0!")
                    return

                if noise_length >= len(self.loaded_matrix):
                    messagebox.showerror(
                        "Помилка",
                        f"Довжина шуму ({noise_length}) має бути менше розміру матриці ({len(self.loaded_matrix)})!"
                    )
                    return

                enc_txt = hill_encrypt_modified(
                    txt,
                    self.loaded_matrix,
                    self.alphabet,
                    self.substitution_mapping,
                    noise_length
                )

            save_file(enc_txt, "encrypted.txt", "Зберегти зашифрований текст")

        except Exception as e:
            messagebox.showerror("Помилка", str(e))