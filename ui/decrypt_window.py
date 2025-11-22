"""
Вікно розшифрування
"""

import tkinter as tk
from tkinter import messagebox
import numpy as np
from config import *
from cipher.hill_cipher import (
    text_to_numbers,
    numbers_to_text,
    hill_decrypt_standard,
    hill_decrypt_modified
)
from utils.file_utils import load_text_file, load_matrix_file, save_file
from data.templates import ALPHABET_UKR


class DecryptWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Розшифровувач")
        self.window.state('zoomed')
        self.window.configure(bg=BG_COLOR)

        self.alphabet = ALPHABET_UKR
        self.alphabet_name = "Український"
        self.loaded_matrix_dec = None
        self.substitution_mapping_dec = []

        self.create_widgets()

    def create_widgets(self):
        """Створення всіх віджетів"""
        # ==================== АЛФАВІТ ====================
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

        # ==================== РЕЖИМ РОЗШИФРУВАННЯ ====================
        mode_frame = tk.Frame(self.window, bg=BG_COLOR)
        mode_frame.pack(pady=5)
        self.decryption_mode = tk.IntVar(value=0)

        self.rb_standard = tk.Radiobutton(
            mode_frame,
            text="Стандартне розшифрування",
            variable=self.decryption_mode,
            value=0,
            indicatoron=0,
            width=25,
            height=2,
            bg=CELL_BG,
            fg="black",
            command=self.toggle_subst_frame
        )
        self.rb_standard.pack(side="left", padx=5)

        self.rb_modified = tk.Radiobutton(
            mode_frame,
            text="Модифіковане розшифрування",
            variable=self.decryption_mode,
            value=1,
            indicatoron=0,
            width=25,
            height=2,
            bg=CELL_BG,
            fg="black",
            command=self.toggle_subst_frame
        )
        self.rb_modified.pack(side="left", padx=5)

        # ==================== ПІДСТАНОВКА ====================
        self.subst_frame = tk.Frame(self.window, bg=BG_COLOR)

        tk.Label(
            self.subst_frame,
            text="Підстановка:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=2)

        # Клітинка для назви підстановки
        subst_cell = tk.Frame(
            self.subst_frame,
            width=200,
            height=30,
            bd=1,
            relief="solid",
            bg=CELL_BG
        )
        subst_cell.pack(side="left", padx=2)
        subst_cell.pack_propagate(False)

        self.subst_name_var = tk.StringVar(value="Відсутня")
        tk.Label(
            subst_cell,
            textvariable=self.subst_name_var,
            bg=CELL_BG,
            font=FONT_BOLD
        ).pack()

        tk.Button(
            self.subst_frame,
            text="Вибрати підстановку",
            command=self.load_substitution
        ).pack(side="left", padx=2)

        # ==================== ДОВЖИНА ШУМУ ====================
        self.noise_frame = tk.Frame(self.window, bg=BG_COLOR)
        tk.Label(
            self.noise_frame,
            text="Довжина шуму:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.noise_length_entry = tk.Entry(self.noise_frame, width=10)
        self.noise_length_entry.insert(0, "0")
        self.noise_length_entry.pack(side="left", padx=5)

        tk.Label(
            self.noise_frame,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_ITALIC
        ).pack(side="left", padx=2)

        # ==================== ЗАШИФРОВАНИЙ ТЕКСТ ====================
        tk.Label(
            self.window,
            text="Зашифрований текст:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(pady=5)

        self.ciphertext_text = tk.Text(
            self.window,
            width=60,
            height=10,
            state="disabled"
        )
        self.ciphertext_text.pack(pady=5)

        tk.Button(
            self.window,
            text="Відкрити текстовий файл",
            command=self.load_text
        ).pack(pady=5)

        # ==================== МАТРИЦЯ ====================
        matrix_label_frame = tk.Frame(self.window, bg=BG_COLOR)
        matrix_label_frame.pack(pady=5)

        tk.Label(
            matrix_label_frame,
            text="Матриця для розшифрування:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.loaded_matrix_var_dec = tk.StringVar(value="None")
        tk.Label(
            matrix_label_frame,
            textvariable=self.loaded_matrix_var_dec,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_NORMAL
        ).pack(side="left", padx=5)

        tk.Button(
            matrix_label_frame,
            text="Завантажити матрицю",
            command=self.load_key_matrix
        ).pack(side="left", padx=5)

        # ==================== КНОПКА РОЗШИФРУВАННЯ ====================
        tk.Button(
            self.window,
            text="Розшифрувати",
            command=self.decrypt,
            font=FONT_BOLD,
            bg=BUTTON_BG
        ).pack(pady=10)

        # Початкова видимість підстановки
        self.toggle_subst_frame()

    def create_alphabet_cell(self, parent, alphabet_name, alphabet_length):
        """Створення інформаційної клітинки для алфавіту"""
        cell = tk.Frame(
            parent,
            width=200,
            height=30,
            bd=1,
            relief="solid",
            bg=CELL_BG
        )
        cell.pack(side="left", padx=2)
        cell.pack_propagate(False)

        label = tk.Label(
            cell,
            text=f"{alphabet_name} ({alphabet_length})",
            bg=CELL_BG,
            font=FONT_BOLD
        )
        label.pack()
        return label

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
        messagebox.showinfo(
            "Інформація",
            f"Алфавіт завантажено:\n{self.alphabet}"
        )

    def toggle_subst_frame(self):
        """Перемикання видимості підстановки та шуму"""
        if self.decryption_mode.get() == 1:
            # Показати фрейм підстановки та шуму після режиму
            self.subst_frame.pack(pady=5, after=self.rb_modified.master)
            self.noise_frame.pack(pady=5, after=self.subst_frame)
        else:
            # Приховати фрейм підстановки та шуму
            self.subst_frame.pack_forget()
            self.noise_frame.pack_forget()

    def load_substitution(self):
        """Завантажити підстановку"""
        from utils.file_utils import load_substitution_file

        result = load_substitution_file()
        if result is None:
            return

        mapping, name = result

        # Перевірка розміру підстановки
        if len(mapping) != len(self.alphabet):
            messagebox.showerror(
                "Помилка",
                f"Розмір підстановки ({len(mapping)}) != розмір алфавіту ({len(self.alphabet)})."
            )
            return

        self.substitution_mapping_dec = mapping
        self.subst_name_var.set(name)
        messagebox.showinfo(
            "Інформація",
            f"Підстановку '{name}' завантажено успішно!"
        )

    def load_text(self):
        """Завантажити текст"""
        text = load_text_file()
        if text:
            self.ciphertext_text.config(state="normal")
            self.ciphertext_text.delete("1.0", tk.END)
            self.ciphertext_text.insert(tk.END, text)
            self.ciphertext_text.config(state="disabled")

    def load_key_matrix(self):
        """Завантажити ключову матрицю"""
        matrix, name = load_matrix_file()
        if matrix is not None:
            self.loaded_matrix_dec = matrix
            self.loaded_matrix_var_dec.set(name if name else "Завантажено")
            messagebox.showinfo(
                "Інформація",
                f"Матриця '{name if name else 'без назви'}' завантажена успішно!\nРозмір: {len(matrix)}x{len(matrix)}"
            )

    def decrypt(self):
        """Розшифрувати текст"""
        # ==================== ВАЛІДАЦІЯ ====================
        if not self.alphabet:
            messagebox.showerror("Помилка", "Алфавіт не завантажено!")
            return

        if self.loaded_matrix_dec is None:
            messagebox.showerror("Помилка", "Завантажте ключову матрицю!")
            return

        # Отримання тексту
        self.ciphertext_text.config(state="normal")
        txt = self.ciphertext_text.get("1.0", tk.END).strip()
        self.ciphertext_text.config(state="disabled")

        if not txt:
            messagebox.showerror("Помилка", "Текст порожній!")
            return

        try:
            # ==================== РОЗШИФРУВАННЯ ====================
            if self.decryption_mode.get() == 0:
                # Стандартне розшифрування
                dec_txt = hill_decrypt_standard(
                    txt,
                    self.loaded_matrix_dec,
                    self.alphabet
                )
            else:
                # Модифіковане розшифрування з підстановкою
                if not self.substitution_mapping_dec:
                    messagebox.showerror("Помилка", "Підстановку не вибрано!")
                    return

                if len(self.substitution_mapping_dec) != len(self.alphabet):
                    messagebox.showerror(
                        "Помилка",
                        f"Розмір підстановки ({len(self.substitution_mapping_dec)}) != розмір алфавіту ({len(self.alphabet)})."
                    )
                    return

                # Отримати довжину шуму
                noise_str = self.noise_length_entry.get().strip()
                noise_length = int(noise_str) if noise_str else 0

                if noise_length < 0:
                    messagebox.showerror("Помилка", "Довжина шуму має бути >= 0!")
                    return

                if noise_length >= len(self.loaded_matrix_dec):
                    messagebox.showerror(
                        "Помилка",
                        f"Довжина шуму ({noise_length}) має бути менше розміру матриці ({len(self.loaded_matrix_dec)})!"
                    )
                    return

                # Розшифрування з підстановкою та шумом
                dec_txt = hill_decrypt_modified(
                    txt,
                    self.loaded_matrix_dec,
                    self.alphabet,
                    self.substitution_mapping_dec,
                    noise_length
                )

            # ==================== ЗБЕРЕЖЕННЯ РЕЗУЛЬТАТУ ====================
            success = save_file(
                dec_txt,
                "decrypted.txt",
                "Зберегти розшифрований текст"
            )

            if success:
                # Показати попередній перегляд результату
                preview = dec_txt[:200] + ("..." if len(dec_txt) > 200 else "")
                messagebox.showinfo(
                    "Успіх",
                    f"Текст розшифровано успішно!\n\nПопередній перегляд:\n{preview}"
                )

        except ValueError as ve:
            messagebox.showerror(
                "Помилка розшифрування",
                f"Не вдалося розшифрувати текст:\n{str(ve)}\n\nПеревірте правильність матриці та алфавіту."
            )
        except Exception as e:
            messagebox.showerror(
                "Помилка",
                f"Виникла несподівана помилка:\n{str(e)}"
            )