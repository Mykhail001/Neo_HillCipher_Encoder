"""
Вікно створення матриці
"""

import tkinter as tk
from tkinter import messagebox
import secrets
import numpy as np
from config import *
from utils.math_utils import determinant, is_prime
from utils.file_utils import save_file, load_matrix_file


class MatrixWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Створення матриці")
        self.window.state('zoomed')
        self.window.configure(bg=BG_COLOR)

        self.mode_var = tk.StringVar(value="standard")
        self.generated_circular_matrix = []
        self.matrix_entries = []

        self.create_widgets()

    def create_widgets(self):
        """Створення всіх віджетів"""
        # Назва матриці
        name_frame = tk.Frame(self.window, bg=BG_COLOR)
        name_frame.pack(pady=5)
        tk.Label(
            name_frame,
            text="Назва матриці:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)
        self.matrix_name_var = tk.StringVar(value="")
        self.matrix_name_entry = tk.Entry(
            name_frame,
            textvariable=self.matrix_name_var,
            font=FONT_NORMAL
        )
        self.matrix_name_entry.pack(side="left", padx=5)

        # Кнопка відкриття матриці
        row2 = tk.Frame(self.window, bg=BG_COLOR)
        row2.pack(pady=5)

        tk.Button(
            row2,
            text="Відкрити матрицю",
            command=self.load_and_fill_matrix
        ).pack(side="top", pady=5)

        # Режими роботи
        mode_frame = tk.Frame(row2, bg=BG_COLOR)
        mode_frame.pack(pady=5)

        self.standard_frame = tk.Frame(self.window, bg=BG_COLOR)
        self.circular_frame = tk.Frame(self.window, bg=BG_COLOR)

        # Створення стандартного режиму
        self.create_standard_mode()

        # Створення параметричного режиму
        self.create_circular_mode()

        # Кнопки перемикання режимів
        self.btn_mode1 = tk.Button(
            mode_frame,
            text="Стандартний режим",
            command=self.show_standard,
            width=25,
            height=2,
            bg=CELL_BG,
            fg="black",
            relief="sunken"
        )
        self.btn_mode1.pack(side="left", padx=5)

        self.btn_mode2 = tk.Button(
            mode_frame,
            text="Параметричний режим",
            command=self.show_circular,
            width=25,
            height=2,
            bg=CELL_BG,
            fg="black",
            relief="raised"
        )
        self.btn_mode2.pack(side="left", padx=5)

        self.show_standard()

    def create_standard_mode(self):
        """Створення стандартного режиму"""
        # Заголовок
        key_label_frame = tk.Frame(self.standard_frame, bg=BG_COLOR)
        key_label_frame.pack(pady=5)
        tk.Label(
            key_label_frame,
            text="Введіть ключову матрицю:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        # Область матриці
        self.matrix_frame = tk.Frame(self.standard_frame, bg=BG_COLOR)
        self.matrix_frame.pack(pady=10)

        # Розмір матриці
        size_frame = tk.Frame(self.standard_frame, bg=BG_COLOR)
        size_frame.pack(pady=5)
        tk.Label(
            size_frame,
            text="Розмір матриці:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)
        self.matrix_size_entry = tk.Entry(size_frame, width=5, font=FONT_NORMAL)
        self.matrix_size_entry.pack(side="left")
        self.matrix_size_entry.insert(0, "2")

        tk.Button(
            size_frame,
            text="Підтвердити",
            command=self.confirm_matrix_size
        ).pack(side="left", padx=5)

        # Визначник
        det_frame = tk.Frame(self.standard_frame, bg=BG_COLOR)
        det_frame.pack(pady=5)
        tk.Label(
            det_frame,
            text="Визначник матриці:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)
        self.det_value_var = tk.StringVar(value="N/A")
        tk.Label(
            det_frame,
            textvariable=self.det_value_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_NORMAL
        ).pack(side="left", padx=5)

        tk.Button(
            det_frame,
            text="Обчислити визначник",
            command=self.calc_det
        ).pack(side="left", padx=5)

        # Кнопка збереження
        tk.Button(
            self.standard_frame,
            text="Зберегти матрицю",
            font=FONT_BOLD,
            bg=BUTTON_BG,
            command=self.save_matrix
        ).pack(pady=10)

        self.confirm_matrix_size()

    def create_circular_mode(self):
        """Створення параметричного режиму"""
        # Поля введення
        self.alpha_entry = self.create_labeled_entry(
            self.circular_frame, "Альфа:"
        )
        self.beta_entry = self.create_labeled_entry(
            self.circular_frame, "Бета:"
        )
        self.alphabet_size_entry = self.create_labeled_entry(
            self.circular_frame, "Розмір алфавіту:"
        )
        self.private_key_entry = self.create_labeled_entry(
            self.circular_frame, "Приватний ключ:"
        )
        self.noise_size_entry = self.create_labeled_entry(
            self.circular_frame, "Розмір шуму:"
        )
        self.signature_entry = self.create_labeled_entry(
            self.circular_frame, "Підпис:"
        )

        # Секція без підпису
        no_sig_frame = tk.Frame(self.circular_frame, bg=BG_COLOR)
        no_sig_frame.pack(pady=5)
        tk.Label(
            no_sig_frame,
            text="Немає підпису?",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_ITALIC
        ).pack(side="left", padx=5)

        tk.Button(
            no_sig_frame,
            text="Створити матрицю і підпис",
            command=self.open_signature_window
        ).pack(pady=10)

        # Кнопка створення матриці
        tk.Button(
            self.circular_frame,
            text="Створити матрицю",
            command=self.create_matrix_directly,
            bg=BUTTON_BG,
            font=FONT_BOLD
        ).pack(pady=10)

    def create_labeled_entry(self, parent, label_text):
        """Створення поля з підписом"""
        frame = tk.Frame(parent, bg=BG_COLOR)
        frame.pack(pady=5)
        tk.Label(
            frame,
            text=label_text,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)
        entry = tk.Entry(frame, width=20, font=FONT_NORMAL)
        entry.pack(side="left", padx=5)
        return entry

    def load_and_fill_matrix(self):
        """Завантаження та заповнення матриці"""
        matrix, name = load_matrix_file()
        if matrix is None:
            return

        self.generated_circular_matrix = matrix
        size = len(matrix)

        if size > MAX_MATRIX_SIZE:
            messagebox.showerror(
                "Помилка",
                f"Матриця занадто велика! Максимум {MAX_MATRIX_SIZE}x{MAX_MATRIX_SIZE}."
            )
            return

        # Пересоздаємо поля вводу
        if (len(self.matrix_entries) != size or
            (self.matrix_entries and len(self.matrix_entries[0]) != size)):
            for row in self.matrix_entries:
                for entry in row:
                    entry.destroy()
            self.matrix_entries.clear()

            for i in range(size):
                row_entries = []
                for j in range(size):
                    e = tk.Entry(self.matrix_frame, width=5, font=FONT_NORMAL)
                    e.grid(row=i, column=j, padx=2, pady=2)
                    row_entries.append(e)
                self.matrix_entries.append(row_entries)

        # Заповнюємо значення
        for i in range(size):
            for j in range(size):
                self.matrix_entries[i][j].delete(0, tk.END)
                self.matrix_entries[i][j].insert(0, str(matrix[i][j]))

        if name:
            self.matrix_name_var.set(name)

    def confirm_matrix_size(self):
        """Підтвердження розміру матриці"""
        try:
            n = int(self.matrix_size_entry.get())
            if n < 2:
                messagebox.showerror(
                    "Помилка",
                    "Розмір матриці має бути не менше 2."
                )
                return
            if n > MAX_MATRIX_SIZE:
                messagebox.showerror(
                    "Помилка",
                    f"Максимум {MAX_MATRIX_SIZE}x{MAX_MATRIX_SIZE}."
                )
                return
        except ValueError:
            messagebox.showerror("Помилка", "Введіть коректне число.")
            return

        # Створюємо нові поля
        for w in self.matrix_frame.winfo_children():
            w.destroy()
        self.matrix_entries.clear()

        for i in range(n):
            row_entries = []
            for j in range(n):
                e = tk.Entry(self.matrix_frame, width=5, font=FONT_NORMAL)
                e.grid(row=i, column=j, padx=2, pady=2)
                row_entries.append(e)
            self.matrix_entries.append(row_entries)

    def calc_det(self):
        """Обчислення визначника"""
        try:
            mat = [[int(entry.get()) for entry in row]
                   for row in self.matrix_entries]
            d = determinant(mat)
            self.det_value_var.set(str(d))
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка обчислення:\n{e}")

    def open_signature_window(self):
        """Відкрити вікно створення підпису"""
        sig_win = tk.Toplevel(self.circular_frame)
        sig_win.title("Створити підпис")
        sig_win.geometry("400x500")
        sig_win.configure(bg=BG_COLOR)

        signature_var = tk.StringVar(value="")
        filename_var = tk.StringVar(value="")

        # Поля введення
        filename_entry = self.create_labeled_entry(sig_win, "Назва матриці:")
        filename_entry.config(textvariable=filename_var)

        alpha_new = self.create_labeled_entry(sig_win, "Альфа:")
        alphabet_size_new = self.create_labeled_entry(sig_win, "Розмір алфавіту:")
        private_key_new = self.create_labeled_entry(sig_win, "Приватний ключ:")
        noise_size_new = self.create_labeled_entry(sig_win, "Розмір шуму:")

        signature_label = tk.Label(
            sig_win,
            textvariable=signature_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_NORMAL,
            justify="left"
        )
        signature_label.pack(pady=10)

        def generate_signature():
            try:
                alpha = int(alpha_new.get())
                alphabet_size = int(alphabet_size_new.get())
                private_key = int(private_key_new.get())

                # Розмір шуму (за замовчуванням 0)
                noise_str = noise_size_new.get().strip()
                noise_size = int(noise_str) if noise_str else 0
                if noise_size < 0:
                    raise ValueError("Розмір шуму має бути >= 0.")

                if alpha <= 0:
                    raise ValueError("Альфа має бути додатнім числом.")
                if not is_prime(alphabet_size):
                    raise ValueError("Розмір алфавіту має бути простим числом.")
                if not (1 < private_key < alphabet_size - 1):
                    raise ValueError(
                        "Приватний ключ має бути більше 1 і менше (розміру алфавіту - 1)."
                    )

                beta = pow(alpha, private_key, alphabet_size)
                rp = secrets.randbelow(alphabet_size - 3) + 2
                signature = pow(alpha, rp, alphabet_size)
                secret_key = pow(beta, rp, alphabet_size)

                size = secret_key + noise_size

                signature_var.set(
                    f"Бета: {beta}\n"
                    f"Підпис: {signature}\n"
                    f"Секретний ключ: {secret_key}\n"
                    f"Розмір матриці: {size}x{size}"
                )
                first_row = [
                    pow(alpha, pow(secret_key, i, 1000), alphabet_size)
                    for i in range(size)
                ]
                self.generated_circular_matrix = [
                    first_row[-i:] + first_row[:-i] for i in range(size)
                ]

            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        def save_generated_matrix():
            if not self.generated_circular_matrix:
                messagebox.showerror("Помилка", "Матриця не створена.")
                return

            filename = filename_var.get().strip()
            if not filename:
                messagebox.showerror("Помилка", "Введіть назву файлу.")
                return

            content = "\n".join(
                ','.join(map(str, row))
                for row in self.generated_circular_matrix
            )

            if save_file(content, f"Matrix_{filename}.txt", "Зберегти матрицю"):
                sig_win.destroy()

        tk.Button(
            sig_win,
            text="Створити підпис",
            command=generate_signature
        ).pack(pady=10)

        tk.Button(
            sig_win,
            text="Створити матрицю",
            command=save_generated_matrix,
            bg=BUTTON_BG,
            font=FONT_BOLD
        ).pack(pady=10)

    def create_matrix_directly(self):
        """Створити матрицю напряму з параметрів"""
        try:
            alpha = int(self.alpha_entry.get())
            beta = int(self.beta_entry.get())
            alphabet_size = int(self.alphabet_size_entry.get())
            private_key = int(self.private_key_entry.get())
            signature = int(self.signature_entry.get())

            # Розмір шуму (за замовчуванням 0)
            noise_str = self.noise_size_entry.get().strip()
            noise_size = int(noise_str) if noise_str else 0
            if noise_size < 0:
                raise ValueError("Розмір шуму має бути >= 0.")

            if alpha <= 0:
                raise ValueError("Альфа має бути додатнім числом.")
            if not is_prime(alphabet_size):
                raise ValueError("Розмір алфавіту має бути простим числом.")
            if not (1 < private_key < alphabet_size - 1):
                raise ValueError(
                    "Приватний ключ має бути більше 1 і менше (розміру алфавіту - 1)."
                )

            secret_key = pow(signature, private_key, alphabet_size)
            size = secret_key + noise_size
            first_row = [
                pow(alpha, pow(secret_key, i, 1000), alphabet_size)
                for i in range(size)
            ]
            self.generated_circular_matrix = [
                first_row[-i:] + first_row[:-i] for i in range(size)
            ]

            content = "\n".join(
                ','.join(map(str, row))
                for row in self.generated_circular_matrix
            )

            messagebox.showinfo(
                "Інформація",
                f"Секретний ключ: {secret_key}\n"
                f"Довжина шуму: {noise_size}\n"
                f"Розмір матриці: {size}x{size}"
            )

            save_file(
                content,
                f"Matrix_{secret_key}_noise{noise_size}.txt",
                "Зберегти матрицю"
            )

        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def save_matrix(self):
        """Зберегти матрицю"""
        try:
            if self.mode_var.get() == "standard":
                mat = [[int(entry.get()) for entry in row]
                       for row in self.matrix_entries]
            else:
                mat = self.generated_circular_matrix

            name_suffix = self.matrix_name_var.get().strip()
            if not name_suffix:
                messagebox.showerror("Помилка", "Введіть назву матриці!")
                return

            content = "\n".join(','.join(str(x) for x in row) for row in mat)
            save_file(content, f"Matrix_{name_suffix}.txt", "Зберегти матрицю")

        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти:\n{e}")

    def show_standard(self):
        """Показати стандартний режим"""
        self.mode_var.set("standard")
        self.circular_frame.pack_forget()
        self.standard_frame.pack(pady=5)
        self.btn_mode1.config(relief="sunken")
        self.btn_mode2.config(relief="raised")

    def show_circular(self):
        """Показати параметричний режим"""
        self.mode_var.set("circular")
        self.standard_frame.pack_forget()
        self.circular_frame.pack(pady=5)
        self.btn_mode1.config(relief="raised")
        self.btn_mode2.config(relief="sunken")