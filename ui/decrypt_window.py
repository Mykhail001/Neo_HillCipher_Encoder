"""
Вікно розшифрування
"""

import os
import time
import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np
from config import *
from cipher.hill_cipher import (
    text_to_numbers,
    numbers_to_text,
    hill_decrypt_standard,
    hill_decrypt_modified
)
from utils.file_utils import (
    load_text_file, load_matrix_file, save_file,
    remove_padding, base64_to_file, DEFAULT_PADDING_SYMBOL
)
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
            selectcolor=ACCENT_COLOR,
            activebackground=BUTTON_BG,
            relief="raised",
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
            selectcolor=ACCENT_COLOR,
            activebackground=BUTTON_BG,
            relief="raised",
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
        self.subst_name_var = tk.StringVar(value="Відсутня")
        tk.Label(
            self.subst_frame,
            textvariable=self.subst_name_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=2)

        tk.Button(
            self.subst_frame,
            text="Вибрати підстановку",
            command=self.load_substitution,
            bg=CELL_BG,
            fg="black"
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

        self.noise_length_entry = tk.Entry(self.noise_frame, width=10, bg=CELL_BG, font=("Arial", 11))
        self.noise_length_entry.insert(0, "0")
        self.noise_length_entry.pack(side="left", padx=5)

        tk.Label(
            self.noise_frame,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_ITALIC
        ).pack(side="left", padx=2)

        # ==================== ТЕКСТ (для режиму тексту) ====================
        self.text_frame = tk.Frame(self.window, bg=BG_COLOR)

        tk.Label(
            self.text_frame,
            text="Зашифрований текст:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(pady=5)

        self.ciphertext_text = tk.Text(
            self.text_frame,
            width=60,
            height=10,
            state="disabled",
            bg=CELL_BG,
            font=("Arial", 11)
        )
        self.ciphertext_text.pack(pady=5)

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
            text="Зашифрований файл:",
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
            text="(той самий, що при шифруванні)",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_ITALIC
        ).pack(side="left", padx=5)

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
            command=self.load_key_matrix,
            bg=CELL_BG,
            fg="black"
        ).pack(side="left", padx=5)

        # ==================== КНОПКА РОЗШИФРУВАННЯ ====================
        self.decrypt_btn = tk.Button(
            self.window,
            text="Розшифрувати текст",
            command=self.decrypt,
            font=FONT_BOLD,
            bg=BUTTON_BG,
            fg=FG_COLOR
        )
        self.decrypt_btn.pack(pady=10)

        # Початкова видимість підстановки
        self.toggle_subst_frame()
        self.toggle_input_mode()

    def toggle_input_mode(self):
        """Перемикання між режимом тексту та файлу"""
        if self.input_mode.get() == 0:
            # Режим тексту
            self.file_frame.pack_forget()
            self.decrypt_btn.pack_forget()
            self.text_frame.pack(pady=5)
            self.decrypt_btn.pack(pady=10)
            self.decrypt_btn.config(text="Розшифрувати текст")
        else:
            # Режим файлу
            self.text_frame.pack_forget()
            self.decrypt_btn.pack_forget()
            self.file_frame.pack(pady=5)
            self.decrypt_btn.pack(pady=10)
            self.decrypt_btn.config(text="Розшифрувати файл")

    def select_file(self):
        """Вибір файлу для розшифрування"""
        fpath = filedialog.askopenfilename(
            title="Виберіть зашифрований файл",
            filetypes=[
                ("Encrypted Files", "*.encrypted"),
                ("All Files", "*.*")
            ]
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
                self.file_info_var.set(f"Розмір: {file_size} байт")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{str(e)}")

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

    def decrypt(self):
        """Розшифрувати текст або файл"""
        if self.input_mode.get() == 0:
            self.decrypt_text()
        else:
            self.decrypt_file()

    def decrypt_text(self):
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
            start_time = time.time()

            if self.decryption_mode.get() == 0:
                # Стандартне розшифрування
                ciphertext_numbers = text_to_numbers(txt, self.alphabet)
                dec_numbers = hill_decrypt_standard(
                    ciphertext_numbers,
                    self.loaded_matrix_dec,
                    self.alphabet
                )
                dec_txt = numbers_to_text(dec_numbers, self.alphabet)
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

            end_time = time.time()
            decryption_time = end_time - start_time
            print(f"Час розшифрування тексту: {decryption_time:.6f} секунд")

            # ==================== ЗБЕРЕЖЕННЯ РЕЗУЛЬТАТУ ====================
            success = save_file(
                dec_txt,
                "text_decrypted.txt",
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

    def decrypt_file(self):
        """Розшифрувати файл"""
        # ==================== ВАЛІДАЦІЯ ====================
        if not self.alphabet:
            messagebox.showerror("Помилка", "Алфавіт не завантажено!")
            return

        if self.loaded_matrix_dec is None:
            messagebox.showerror("Помилка", "Завантажте ключову матрицю!")
            return

        if not self.selected_file_path:
            messagebox.showerror("Помилка", "Оберіть зашифрований файл!")
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
            # 1. Читаємо зашифрований файл
            with open(self.selected_file_path, "r", encoding="utf-8") as f:
                encrypted_text = f.read()

            encrypted_length = len(encrypted_text)

            # 2. Розшифровуємо
            start_time = time.time()

            if self.decryption_mode.get() == 0:
                # Стандартне розшифрування
                ciphertext_numbers = text_to_numbers(encrypted_text, self.alphabet)
                dec_numbers = hill_decrypt_standard(
                    ciphertext_numbers,
                    self.loaded_matrix_dec,
                    self.alphabet
                )
                decrypted_text = numbers_to_text(dec_numbers, self.alphabet)
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

                decrypted_text = hill_decrypt_modified(
                    encrypted_text,
                    self.loaded_matrix_dec,
                    self.alphabet,
                    self.substitution_mapping_dec,
                    noise_length
                )

            end_time = time.time()
            decryption_time = end_time - start_time
            print(f"Час розшифрування файлу: {decryption_time:.6f} секунд")

            # 3. Видаляємо padding
            clean_text, padding_removed = remove_padding(decrypted_text, padding_symbol)

            # 4. Вибираємо папку для збереження
            output_dir = filedialog.askdirectory(
                title="Виберіть папку для збереження відновленого файлу"
            )

            if not output_dir:
                return

            base_name = os.path.splitext(os.path.basename(self.selected_file_path))[0]
            # Видаляємо .encrypted з назви якщо є
            if base_name.endswith('.encrypted'):
                base_name = base_name[:-10]

            success, result = base64_to_file(clean_text, output_dir, base_name)

            if success:
                restored_size = os.path.getsize(result)

                messagebox.showinfo(
                    "Успіх",
                    f"Файл розшифровано та відновлено успішно!\n\n"
                    f"Зашифрований файл: {os.path.basename(self.selected_file_path)}\n"
                    f"Довжина зашифрованого: {encrypted_length} символів\n\n"
                    f"Видалено padding '{padding_symbol}': {padding_removed} символів\n"
                    f"Base64 довжина: {len(clean_text)} символів\n\n"
                    f"Відновлено: {os.path.basename(result)}\n"
                    f"Розмір відновленого: {restored_size} байт"
                )
            else:
                messagebox.showerror(
                    "Помилка",
                    f"Не вдалося відновити файл з Base64:\n{result}"
                )

        except ValueError as ve:
            messagebox.showerror(
                "Помилка розшифрування",
                f"Не вдалося розшифрувати файл:\n{str(ve)}\n\nПеревірте правильність матриці та алфавіту."
            )
        except Exception as e:
            messagebox.showerror(
                "Помилка",
                f"Виникла несподівана помилка:\n{str(e)}"
            )
