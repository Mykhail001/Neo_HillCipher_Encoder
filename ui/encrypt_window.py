"""
Вікно шифрування
"""

import os
import time
import tkinter as tk
from tkinter import messagebox, filedialog
from config import *
from cipher.hill_cipher import (
    text_to_numbers,
    hill_encrypt_standard,
    hill_encrypt_modified
)
from utils.file_utils import (
    load_text_file, load_matrix_file, save_file,
    file_to_base64_with_marker, add_padding_for_matrix,
    validate_text_for_alphabet, DEFAULT_PADDING_SYMBOL
)
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
        self.selected_file_path = None

        self.create_widgets()

    def create_widgets(self):
        """Створення всіх віджетів"""
        # ==================== РЕЖИМ ВВОДУ (ТЕКСТ/ФАЙЛ) ====================
        input_mode_frame = tk.Frame(self.window, bg=BG_COLOR)
        input_mode_frame.pack(pady=10)

        tk.Label(
            input_mode_frame,
            text="Режим вводу:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.input_mode = tk.IntVar(value=0)  # 0 = текст, 1 = файл

        tk.Radiobutton(
            input_mode_frame,
            text="Текст",
            variable=self.input_mode,
            value=0,
            indicatoron=0,
            width=15,
            height=2,
            bg=CELL_BG,
            fg="black",
            selectcolor=ACCENT_COLOR,
            activebackground=BUTTON_BG,
            relief="raised",
            command=self.toggle_input_mode
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            input_mode_frame,
            text="Файл",
            variable=self.input_mode,
            value=1,
            indicatoron=0,
            width=15,
            height=2,
            bg=CELL_BG,
            fg="black",
            selectcolor=ACCENT_COLOR,
            activebackground=BUTTON_BG,
            relief="raised",
            command=self.toggle_input_mode
        ).pack(side="left", padx=5)

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

        self.alphabet_btn = tk.Button(
            top_frame,
            text="Відкрити алфавіт",
            command=self.open_alphabet_file,
            bg=CELL_BG,
            fg="black"
        )
        self.alphabet_btn.pack(side="left", padx=5)

        # ==================== РЕЖИМ ШИФРУВАННЯ ====================
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

        # ==================== ПІДСТАНОВКА ====================
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

        # ==================== ДОВЖИНА ШУМУ ====================
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

        # ==================== ТЕКСТ (для режиму тексту) ====================
        self.text_frame = tk.Frame(self.window, bg=BG_COLOR)

        tk.Label(
            self.text_frame,
            text="Текст:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(pady=5)

        self.input_text = tk.Text(self.text_frame, width=60, height=10, state="disabled", bg=CELL_BG, font=("Arial", 11))
        self.input_text.pack(pady=5)

        tk.Button(
            self.text_frame,
            text="Відкрити текстовий файл",
            command=self.load_text,
            bg=CELL_BG,
            fg="black"
        ).pack(pady=5)

        self.text_frame.pack(pady=5)

        # ==================== ФАЙЛ (для режиму файлу) ====================
        self.file_frame = tk.Frame(self.window, bg=BG_COLOR)

        tk.Label(
            self.file_frame,
            text="Файл для шифрування:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(pady=5)

        file_select_frame = tk.Frame(self.file_frame, bg=BG_COLOR)
        file_select_frame.pack(pady=5)

        self.file_path_var = tk.StringVar(value="Файл не обрано")
        tk.Label(
            file_select_frame,
            textvariable=self.file_path_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_NORMAL
        ).pack(side="left", padx=5)

        tk.Button(
            file_select_frame,
            text="Обрати файл",
            command=self.select_file,
            bg=CELL_BG,
            fg="black"
        ).pack(side="left", padx=5)

        # Інформація про файл
        self.file_info_var = tk.StringVar(value="")
        tk.Label(
            self.file_frame,
            textvariable=self.file_info_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_ITALIC
        ).pack(pady=5)

        # Символ padding
        padding_frame = tk.Frame(self.file_frame, bg=BG_COLOR)
        padding_frame.pack(pady=5)

        tk.Label(
            padding_frame,
            text="Символ padding:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.padding_entry = tk.Entry(padding_frame, width=5, bg=CELL_BG, font=("Arial", 11))
        self.padding_entry.insert(0, DEFAULT_PADDING_SYMBOL)
        self.padding_entry.pack(side="left", padx=5)

        tk.Label(
            padding_frame,
            text="(має бути в алфавіті)",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_ITALIC
        ).pack(side="left", padx=5)

        # ==================== МАТРИЦЯ ====================
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

        # ==================== КНОПКА ШИФРУВАННЯ ====================
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
        self.toggle_input_mode()

    def toggle_input_mode(self):
        """Перемикання між режимом тексту та файлу"""
        if self.input_mode.get() == 0:
            # Режим тексту
            self.file_frame.pack_forget()
            self.encrypt_btn.pack_forget()
            self.text_frame.pack(pady=5)
            self.encrypt_btn.pack(pady=10)
            self.encrypt_btn.config(text="Зашифрувати текст")
        else:
            # Режим файлу
            self.text_frame.pack_forget()
            self.encrypt_btn.pack_forget()
            self.file_frame.pack(pady=5)
            self.encrypt_btn.pack(pady=10)
            self.encrypt_btn.config(text="Зашифрувати файл")

    def select_file(self):
        """Вибір файлу для шифрування"""
        fpath = filedialog.askopenfilename(
            title="Виберіть файл для шифрування"
        )
        if fpath:
            try:
                if not os.path.exists(fpath):
                    messagebox.showerror("Помилка", f"Файл не знайдено:\n{fpath}")
                    return

                self.selected_file_path = fpath
                filename = os.path.basename(fpath)
                self.file_path_var.set(filename)

                # Показуємо інформацію про файл
                file_size = os.path.getsize(fpath)
                ext = os.path.splitext(fpath)[1] or "без розширення"
                self.file_info_var.set(
                    f"Розмір: {file_size} байт | Формат: {ext}"
                )
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{str(e)}")

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
        """Зашифрувати текст або файл"""
        if self.input_mode.get() == 0:
            self.encrypt_text()
        else:
            self.encrypt_file()

    def encrypt_text(self):
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
            start_time = time.time()

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

            end_time = time.time()
            encryption_time = end_time - start_time
            print(f"Час шифрування тексту: {encryption_time:.6f} секунд")

            save_file(enc_txt, "text_encrypted.txt", "Зберегти зашифрований текст")

        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def encrypt_file(self):
        """Зашифрувати файл"""
        if self.loaded_matrix is None:
            messagebox.showerror("Помилка", "Завантажте ключову матрицю!")
            return

        if not self.selected_file_path:
            messagebox.showerror("Помилка", "Оберіть файл для шифрування!")
            return

        # Отримуємо символ padding
        padding_symbol = self.padding_entry.get()
        if not padding_symbol:
            messagebox.showerror("Помилка", "Введіть символ padding!")
            return
        if len(padding_symbol) != 1:
            messagebox.showerror("Помилка", "Символ padding має бути одним символом!")
            return

        try:
            # 1. Конвертуємо файл в Base64 з маркером формату
            base64_text, original_ext = file_to_base64_with_marker(self.selected_file_path)

            # 2. Додаємо padding до кратності розміру матриці
            matrix_size = len(self.loaded_matrix)
            padded_text, padding_count = add_padding_for_matrix(base64_text, matrix_size, padding_symbol)

            # 3. Перевіряємо, чи всі символи є в алфавіті
            is_valid, missing_chars = validate_text_for_alphabet(padded_text, self.alphabet)
            if not is_valid:
                missing_list = sorted(list(missing_chars))
                missing_str = ', '.join([f"'{c}'" for c in missing_list[:20]])
                if len(missing_list) > 20:
                    missing_str += f"... (та ще {len(missing_list) - 20})"

                messagebox.showerror(
                    "Помилка",
                    f"Алфавіт не містить всіх необхідних символів!\n\n"
                    f"Відсутні символи ({len(missing_list)}):\n{missing_str}\n\n"
                    f"Завантажте алфавіт, який містить всі символи Base64:\n"
                    f"A-Z, a-z, 0-9, +, /, =, : та символ padding '{padding_symbol}'"
                )
                return

            # 4. Шифруємо
            start_time = time.time()

            if self.encryption_mode.get() == 0:
                # Стандартне шифрування
                numbers = text_to_numbers(padded_text, self.alphabet)
                enc_numbers = hill_encrypt_standard(
                    numbers,
                    self.loaded_matrix,
                    self.alphabet
                )
                enc_txt = "".join(self.alphabet[num] for num in enc_numbers)
            else:
                # Модифіковане шифрування
                if not self.substitution_mapping:
                    messagebox.showerror("Помилка", "Підстановку не вибрано!")
                    return
                if len(self.substitution_mapping) != len(self.alphabet):
                    messagebox.showerror(
                        "Помилка",
                        f"Розмір підстановки ({len(self.substitution_mapping)}) != розмір алфавіту ({len(self.alphabet)})."
                    )
                    return

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
                    padded_text,
                    self.loaded_matrix,
                    self.alphabet,
                    self.substitution_mapping,
                    noise_length
                )

            end_time = time.time()
            encryption_time = end_time - start_time
            print(f"Час шифрування файлу: {encryption_time:.6f} секунд")

            # 5. Зберігаємо результат
            base_name = os.path.splitext(os.path.basename(self.selected_file_path))[0]
            default_name = f"{base_name}_encrypted"

            file_path = filedialog.asksaveasfilename(
                initialfile=default_name,
                defaultextension=".encrypted",
                filetypes=[("Encrypted Files", "*.encrypted"), ("All Files", "*.*")],
                title="Зберегти зашифрований файл"
            )

            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(enc_txt)

                original_size = os.path.getsize(self.selected_file_path)

                messagebox.showinfo(
                    "Успіх",
                    f"Файл зашифровано успішно!\n\n"
                    f"Оригінальний файл: {os.path.basename(self.selected_file_path)}\n"
                    f"Оригінальний розмір: {original_size} байт\n"
                    f"Оригінальний формат: {original_ext or 'без розширення'}\n\n"
                    f"Base64 довжина: {len(base64_text)} символів\n"
                    f"Додано padding '{padding_symbol}': {padding_count} символів\n"
                    f"Фінальна довжина: {len(enc_txt)} символів\n\n"
                    f"Збережено: {os.path.basename(file_path)}"
                )

        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зашифрувати файл:\n{str(e)}")
