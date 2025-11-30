"""
Вікно створення підстановки
"""

import tkinter as tk
from tkinter import messagebox
from collections import Counter
from config import *
from cipher.substitution import (
    generate_random_substitution,
    validate_substitution,
    substitution_to_string,
    string_to_substitution
)
from utils.file_utils import save_file
from data.templates import ALPHABET_UKR


class SubstitutionWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Створення підстановки")
        self.window.state('zoomed')
        self.window.configure(bg=BG_COLOR)

        self.create_widgets()

    def create_widgets(self):
        """Створення всіх віджетів"""
        # Назва підстановки
        name_frame = tk.Frame(self.window, bg=BG_COLOR)
        name_frame.pack(pady=5)
        tk.Label(
            name_frame,
            text="Назва підстановки: ",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)
        self.substitution_name_entry = tk.Entry(name_frame, width=20, bg=CELL_BG, font=("Arial", 11))
        self.substitution_name_entry.pack(side="left")

        # Опції
        options_frame = tk.Frame(self.window, bg=BG_COLOR)
        options_frame.pack(pady=5)

        tk.Button(
            options_frame,
            text="Шаблони",
            command=self.open_substitution_templates,
            bg=CELL_BG,
            fg="black"
        ).pack(side="left", padx=5)

        tk.Button(
            options_frame,
            text="Відкрити підстановку",
            command=self.open_existing_substitution,
            bg=CELL_BG,
            fg="black"
        ).pack(side="left", padx=5)

        # Розмір підстановки
        size_frame = tk.Frame(self.window, bg=BG_COLOR)
        size_frame.pack(pady=10)

        tk.Label(
            size_frame,
            text="Розмір підстановки:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.size_entry = tk.Entry(size_frame, width=10, bg=CELL_BG, font=("Arial", 11))
        self.size_entry.insert(0, "33")
        self.size_entry.pack(side="left", padx=5)

        tk.Button(
            size_frame,
            text="Застосувати розмір",
            command=self.apply_size,
            bg=CELL_BG,
            fg="black"
        ).pack(side="left", padx=5)

        # Поле для вводу підстановки
        tk.Label(
            self.window,
            text="Підстановка (числа через пробіл або кому):",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(pady=5)

        self.substitution_text = tk.Text(
            self.window,
            font=("Consolas", 14),
            width=70,
            height=8,
            wrap="word",
            bg=CELL_BG
        )
        self.substitution_text.pack(pady=5)

        # Bind для оновлення інфо
        self.substitution_text.bind("<KeyRelease>", self.update_info)

        # Інформаційний лейбл
        self.info_label = tk.Label(
            self.window,
            text="Поточна довжина: 0 чисел",
            bg=BG_COLOR,
            fg=FG_COLOR
        )
        self.info_label.pack(pady=(0, 5))

        # Кнопка генерації
        tk.Button(
            self.window,
            text="Згенерувати випадкову підстановку",
            command=self.generate_random_substitution,
            bg=CELL_BG,
            fg="black",
            font=FONT_BOLD
        ).pack(pady=5)

        # Кнопка збереження
        tk.Button(
            self.window,
            text="Створити підстановку",
            command=self.save_substitution,
            font=FONT_BOLD,
            bg=BUTTON_BG,
            fg=FG_COLOR
        ).pack(pady=10)

    def format_numbers(self, numbers, size):
        """Форматування чисел з динамічною кількістю на рядок"""
        if not numbers:
            return ""

        # Визначаємо максимальну кількість цифр для чисел
        max_digits = len(str(size - 1)) if size > 0 else 1
        # Ширина текстового поля - 70 символів
        # Кожне число займає max_digits + 1 (пробіл)
        numbers_per_line = max(1, 70 // (max_digits + 1))

        formatted = []
        for i in range(0, len(numbers), numbers_per_line):
            formatted.append(" ".join(map(str, numbers[i:i+numbers_per_line])))

        return "\n".join(formatted)

    def parse_numbers(self):
        """Парсинг чисел з текстового поля"""
        text = self.substitution_text.get("1.0", "end-1c").strip()
        if not text:
            return []

        # Замінюємо коми та інші роздільники на пробіли
        text = text.replace(',', ' ').replace(';', ' ').replace('\n', ' ')

        numbers = []
        for part in text.split():
            part = part.strip()
            if part:
                try:
                    numbers.append(int(part))
                except ValueError:
                    pass

        return numbers

    def get_non_numeric_parts(self):
        """Отримати список нечислових частин з текстового поля"""
        text = self.substitution_text.get("1.0", "end-1c").strip()
        if not text:
            return []

        # Замінюємо коми та інші роздільники на пробіли
        text = text.replace(',', ' ').replace(';', ' ').replace('\n', ' ')

        non_numeric = []
        for part in text.split():
            part = part.strip()
            if part:
                try:
                    int(part)
                except ValueError:
                    non_numeric.append(part)

        return non_numeric

    def update_info(self, event=None):
        """Оновлення інформації про підстановку"""
        numbers = self.parse_numbers()
        non_numeric = self.get_non_numeric_parts()

        max_val = max(numbers) if numbers else 0
        size = int(self.size_entry.get()) if self.size_entry.get().strip() else 0

        info_text = f"Поточна довжина: {len(numbers)} чисел"
        if numbers:
            info_text += f" | Макс. значення: {max_val}"
            if size > 0 and max_val >= size:
                info_text += f" (має бути < {size})"

        # Перевірка на від'ємні значення
        negative_values = [n for n in numbers if n < 0]
        if negative_values:
            info_text += f" | Від'ємні: {len(negative_values)}"

        # Перевірка на дублікати
        if numbers:
            counts = Counter(numbers)
            duplicates = {val: cnt for val, cnt in counts.items() if cnt > 1}
            if duplicates:
                dup_count = sum(cnt - 1 for cnt in duplicates.values())
                info_text += f" | Дублікати: {dup_count}"

        if non_numeric:
            info_text += f" | Нечислові значення: {', '.join(non_numeric[:5])}"
            if len(non_numeric) > 5:
                info_text += f"... (+{len(non_numeric) - 5})"

        self.info_label.config(text=info_text)

    def apply_size(self):
        """Застосування заданого розміру"""
        try:
            size = int(self.size_entry.get())
            if size <= 0:
                raise ValueError

            numbers = self.parse_numbers()

            # Видаляємо числа що виходять за межі
            filtered = [n for n in numbers if 0 <= n < size]

            if len(filtered) != len(numbers):
                self.substitution_text.delete("1.0", tk.END)
                self.substitution_text.insert("1.0", " ".join(map(str, filtered)))
                messagebox.showinfo(
                    "Інформація",
                    f"Видалено {len(numbers) - len(filtered)} чисел, що виходили за межі діапазону [0, {size-1}]"
                )

            self.update_info()

        except ValueError:
            messagebox.showerror("Помилка", "Введіть коректне число для розміру!")

    def generate_random_substitution(self):
        """Генерація випадкової підстановки"""
        try:
            size = int(self.size_entry.get())
            if size <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Помилка", "Спочатку введіть коректний розмір!")
            return

        # Генерація унікальних чисел від 0 до size-1
        numbers = generate_random_substitution(size)

        # Форматуємо з динамічною кількістю на рядок
        self.substitution_text.delete("1.0", tk.END)
        self.substitution_text.insert("1.0", self.format_numbers(numbers, size))
        self.update_info()

    def open_substitution_templates(self):
        """Відкрити шаблони підстановки"""
        temp_win = tk.Toplevel(self.window)
        temp_win.title("Шаблони підстановки")
        temp_win.geometry("250x150")
        temp_win.configure(bg=BG_COLOR)

        listbox = tk.Listbox(temp_win, selectmode="single", bg=CELL_BG)
        templates = ["Зміщений український", "Зміщений англійський", "Зміщений Base64"]
        for tmpl in templates:
            listbox.insert(tk.END, tmpl)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        def on_select(event):
            sel = listbox.curselection()
            if sel:
                template_name = listbox.get(sel[0])
                if template_name == "Зміщений український":
                    size = 33
                elif template_name == "Зміщений англійський":
                    size = 26
                else:  # Зміщений Base64
                    size = 67

                self.size_entry.delete(0, tk.END)
                self.size_entry.insert(0, str(size))

                # Зміщення на 1: [1, 2, 3, ..., size-1, 0]
                numbers = list(range(1, size)) + [0]

                # Форматуємо з динамічною кількістю на рядок
                self.substitution_text.delete("1.0", tk.END)
                self.substitution_text.insert("1.0", self.format_numbers(numbers, size))
                self.update_info()
                temp_win.destroy()

        listbox.bind("<Double-Button-1>", on_select)

        tk.Button(
            temp_win,
            text="Вибрати",
            command=lambda: on_select(None),
            bg=CELL_BG,
            fg="black"
        ).pack(pady=5)

    def open_existing_substitution(self):
        """Відкрити існуючу підстановку"""
        from tkinter import filedialog

        fpath = filedialog.askopenfilename(
            title="Відкрити підстановку",
            filetypes=[("Text Files", "*.txt")]
        )
        if not fpath:
            return

        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = f.read().strip()

            if not data:
                messagebox.showerror("Помилка", "Файл порожній!")
                return

            substitution = string_to_substitution(data)

            size = len(substitution)
            self.size_entry.delete(0, tk.END)
            self.size_entry.insert(0, str(size))

            # Форматуємо з динамічною кількістю на рядок
            self.substitution_text.delete("1.0", tk.END)
            self.substitution_text.insert("1.0", self.format_numbers(substitution, size))
            self.update_info()

            messagebox.showinfo("Успіх", f"Підстановку завантажено!\nРозмір: {len(substitution)}")

        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{e}")

    def save_substitution(self):
        """Зберегти підстановку"""
        numbers = self.parse_numbers()
        non_numeric = self.get_non_numeric_parts()

        # Перевірка на нечислові значення
        if non_numeric:
            messagebox.showerror(
                "Помилка",
                f"Підстановка має містити лише числа!\n"
                f"Знайдено нечислові значення: {', '.join(non_numeric[:10])}"
                + (f"... (+{len(non_numeric) - 10})" if len(non_numeric) > 10 else "")
            )
            return

        if not numbers:
            messagebox.showerror("Помилка", "Підстановка порожня.")
            return

        try:
            size = int(self.size_entry.get())
            if size <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Помилка", "Некоректний розмір підстановки!")
            return

        # Перевірка розміру
        if len(numbers) != size:
            messagebox.showerror(
                "Помилка",
                f"Кількість чисел ({len(numbers)}) не відповідає розміру ({size})!"
            )
            return

        # Перевірка діапазону
        for v in numbers:
            if v < 0 or v >= size:
                messagebox.showerror(
                    "Помилка",
                    f"Число {v} виходить за межі діапазону [0, {size-1}]!"
                )
                return

        # Валідація (перевірка унікальності)
        is_valid, error_msg = validate_substitution(numbers)
        if not is_valid:
            messagebox.showerror("Помилка", f"Некоректна підстановка:\n{error_msg}")
            return

        # Збереження
        substitution_name = (
            self.substitution_name_entry.get().strip() or "Substitution_Auto"
        )

        content = substitution_to_string(numbers)
        save_file(
            content,
            f"Substitution_{substitution_name}.txt",
            "Зберегти підстановку"
        )