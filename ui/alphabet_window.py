"""
Вікно створення алфавіту
"""

import tkinter as tk
from tkinter import messagebox
from config import *
from data.templates import ALPHABET_TEMPLATES, ALPHABET_UKR
from utils.file_utils import load_alphabet_file, save_file


class AlphabetWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Створення алфавіту")
        self.window.state('zoomed')
        self.window.configure(bg=BG_COLOR)

        self.alphabet = ALPHABET_UKR

        self.create_widgets()

    def create_widgets(self):
        """Створення всіх віджетів"""
        # Назва шаблону
        name_frame = tk.Frame(self.window, bg=BG_COLOR)
        name_frame.pack(pady=5)
        tk.Label(
            name_frame,
            text="Назва шаблону: ",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)
        self.template_name_entry = tk.Entry(name_frame, width=20, bg=CELL_BG, font=("Arial", 11))
        self.template_name_entry.pack(side="left")

        # Кнопки
        buttons_frame = tk.Frame(self.window, bg=BG_COLOR)
        buttons_frame.pack(pady=5)

        tk.Button(
            buttons_frame,
            text="Шаблони",
            command=self.open_templates_list,
            bg=CELL_BG,
            fg="black"
        ).pack(side="left", padx=5)

        tk.Button(
            buttons_frame,
            text="Відкрити алфавіт",
            command=self.open_alphabet_file,
            bg=CELL_BG,
            fg="black"
        ).pack(side="left", padx=5)

        # Розмір алфавіту
        size_frame = tk.Frame(self.window, bg=BG_COLOR)
        size_frame.pack(pady=10)

        tk.Label(
            size_frame,
            text="Розмір алфавіту: ",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.size_entry = tk.Entry(size_frame, width=10, bg=CELL_BG, font=("Arial", 11))
        self.size_entry.insert(0, str(len(self.alphabet)))
        self.size_entry.pack(side="left", padx=5)

        tk.Button(
            size_frame,
            text="Застосувати розмір",
            command=self.apply_size,
            bg=CELL_BG,
            fg="black"
        ).pack(side="left", padx=5)

        # Поле для вводу алфавіту
        tk.Label(
            self.window,
            text="Алфавіт:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(pady=5)

        self.alphabet_text = tk.Text(
            self.window,
            font=("Consolas", 16),
            width=60,
            height=5,
            wrap="char",
            bg=CELL_BG
        )
        self.alphabet_text.pack(pady=5)
        self.alphabet_text.insert("1.0", self.alphabet)

        # Bind для оновлення інфо та валідації
        self.alphabet_text.bind("<KeyRelease>", self.update_info)
        self.alphabet_text.bind("<KeyPress>", self.validate_text_length)

        # Інформаційний лейбл
        self.info_label = tk.Label(
            self.window,
            text=f"Поточна довжина: {len(self.alphabet)} символів",
            bg=BG_COLOR,
            fg=FG_COLOR
        )
        self.info_label.pack(pady=(0, 5))

        # Кнопка збереження
        tk.Button(
            self.window,
            text="Зберегти шаблон",
            font=FONT_BOLD,
            bg=BUTTON_BG,
            fg=FG_COLOR,
            command=self.save_template
        ).pack(pady=20)

        self.populate_mapping(self.alphabet)

    def populate_mapping(self, alph_str):
        """Заповнення текстового поля алфавітом (deprecated, тепер не потрібно)"""
        pass

    def validate_text_length(self, event):
        """Перевірка довжини тексту перед введенням"""
        # Ігноруємо службові клавіші
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down',
                            'Home', 'End', 'Tab', 'Return', 'Control_L', 'Control_R',
                            'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R'):
            return

        try:
            max_length = int(self.size_entry.get())
            current_text = self.alphabet_text.get("1.0", "end-1c")

            # Якщо вже досягнуто ліміту, блокуємо введення
            if len(current_text) >= max_length:
                return "break"
        except (ValueError, tk.TclError):
            pass

    def update_info(self, event=None):
        """Оновлення інформації про довжину алфавіту"""
        current_text = self.alphabet_text.get("1.0", "end-1c")
        self.info_label.config(text=f"Поточна довжина: {len(current_text)} символів")

    def apply_size(self):
        """Застосування заданого розміру"""
        try:
            size = int(self.size_entry.get())
            if size <= 0:
                raise ValueError

            current_text = self.alphabet_text.get("1.0", "end-1c")

            if len(current_text) > size:
                # Обрізаємо
                self.alphabet_text.delete("1.0", tk.END)
                self.alphabet_text.insert("1.0", current_text[:size])

            self.update_info()

        except ValueError:
            messagebox.showerror("Помилка", "Введіть коректне число для розміру!")

    def open_templates_list(self):
        """Відкрити список шаблонів"""
        temp_win = tk.Toplevel(self.window)
        temp_win.title("Шаблони алфавітів")
        temp_win.geometry("200x150")

        listbox = tk.Listbox(temp_win, selectmode="single")
        for key in ALPHABET_TEMPLATES:
            listbox.insert(tk.END, key)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        def on_double_click(event):
            sel = listbox.curselection()
            if not sel:
                return
            temp_name = listbox.get(sel[0])
            template_alphabet = ALPHABET_TEMPLATES[temp_name]
            self.alphabet_text.delete("1.0", tk.END)
            self.alphabet_text.insert("1.0", template_alphabet)
            self.size_entry.delete(0, tk.END)
            self.size_entry.insert(0, str(len(template_alphabet)))
            self.update_info()
            temp_win.destroy()

        listbox.bind("<Double-Button-1>", on_double_click)
        tk.Button(
            temp_win,
            text="Вибрати",
            command=lambda: on_double_click(None)
        ).pack(pady=5)

    def open_alphabet_file(self):
        """Відкрити файл алфавіту"""
        result = load_alphabet_file()
        if result is None:
            return

        content, name = result
        self.alphabet = content
        self.alphabet_text.delete("1.0", tk.END)
        self.alphabet_text.insert("1.0", content)
        self.size_entry.delete(0, tk.END)
        self.size_entry.insert(0, str(len(content)))
        self.update_info()
        messagebox.showinfo(
            "Інформація",
            f"Алфавіт завантажено:\n{self.alphabet}"
        )

    def save_template(self):
        """Зберегти алфавіт"""
        # НЕ конвертуємо в upper() - це дозволяє зберігати алфавіти з
        # великими та малими літерами (наприклад, Base64)
        alphabet_text = self.alphabet_text.get("1.0", "end-1c")

        if not alphabet_text:
            messagebox.showerror("Помилка", "Алфавіт порожній.")
            return

        letters = list(alphabet_text)

        if len(set(letters)) != len(letters):
            messagebox.showerror(
                "Помилка",
                "Алфавіт містить повторювані символи!"
            )
            return

        template_name = self.template_name_entry.get().strip() or "Alphabet_Auto"
        save_file(
            alphabet_text,
            f"Alphabet_{template_name}.txt",
            "Зберегти алфавіт"
        )