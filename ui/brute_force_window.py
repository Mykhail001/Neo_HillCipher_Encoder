"""
Вікно брутфорсу для злому шифру Хілла
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np
import threading
import itertools
import time
from config import *
from cipher.hill_cipher import (
    text_to_numbers,
    numbers_to_text,
    hill_decrypt_standard,
    hill_decrypt_modified
)
from utils.file_utils import load_text_file, save_file
from utils.math_utils import determinant_int, mod_inverse
from data.templates import ALPHABET_UKR


class BruteForceWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Брутфорс")
        self.window.state('zoomed')
        self.window.configure(bg=BG_COLOR)

        self.alphabet = ALPHABET_UKR
        self.alphabet_name = "Український"

        # Стан брутфорсу
        self.is_running = False
        self.is_paused = False
        self.brute_threads = []
        self.attempts_count = 0
        self.successful_attempts = 0  # Кількість успішних спроб (з оберненою матрицею)
        self.results = []  # Список знайдених результатів (accuracy, matrix, params, decrypted_text)
        self.lock = threading.Lock()  # Для синхронізації потоків

        self.create_widgets()

    def create_widgets(self):
        """Створення всіх віджетів"""
        # ==================== ГОЛОВНИЙ КОНТЕЙНЕР ====================
        main_container = tk.Frame(self.window, bg=BG_COLOR)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # ==================== ЛІВА ПАНЕЛЬ ====================
        left_panel = tk.Frame(main_container, bg=BG_COLOR, width=450)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        left_panel.pack_propagate(False)

        # --- Заголовок лівої панелі (центрований) ---
        tk.Label(
            left_panel,
            text="Налаштування брутфорсу",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        # --- Режим брутфорсу (центрований) ---
        mode_frame = tk.Frame(left_panel, bg=BG_COLOR)
        mode_frame.pack(pady=10)

        tk.Label(
            mode_frame,
            text="Режим:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.brute_mode = tk.IntVar(value=0)  # 0 = стандартний, 1 = модифікований

        tk.Radiobutton(
            mode_frame,
            text="Стандартний",
            variable=self.brute_mode,
            value=0,
            indicatoron=0,
            width=15,
            height=2,
            bg=CELL_BG,
            fg="black",
            selectcolor=ACCENT_COLOR,
            activebackground=BUTTON_BG,
            relief="raised",
            command=self.toggle_modified_options
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            mode_frame,
            text="Модифікований",
            variable=self.brute_mode,
            value=1,
            indicatoron=0,
            width=15,
            height=2,
            bg=CELL_BG,
            fg="black",
            selectcolor=ACCENT_COLOR,
            activebackground=BUTTON_BG,
            relief="raised",
            command=self.toggle_modified_options
        ).pack(side="left", padx=5)

        # --- Алфавіт (центрований) ---
        alphabet_frame = tk.Frame(left_panel, bg=BG_COLOR)
        alphabet_frame.pack(pady=10)

        tk.Label(
            alphabet_frame,
            text="Алфавіт:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.alphabet_info_var = tk.StringVar(value=f"{self.alphabet_name} ({len(self.alphabet)})")
        tk.Label(
            alphabet_frame,
            textvariable=self.alphabet_info_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_NORMAL
        ).pack(side="left", padx=5)

        tk.Button(
            alphabet_frame,
            text="Відкрити алфавіт",
            command=self.open_alphabet_file,
            bg=CELL_BG,
            fg="black"
        ).pack(side="left", padx=5)

        # --- Розмір матриці (центрований) ---
        matrix_size_frame = tk.Frame(left_panel, bg=BG_COLOR)
        matrix_size_frame.pack(pady=10)

        tk.Label(
            matrix_size_frame,
            text="Розмір матриці:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.matrix_size_var = tk.IntVar(value=2)
        tk.Spinbox(
            matrix_size_frame,
            from_=2,
            to=4,
            textvariable=self.matrix_size_var,
            width=5,
            font=FONT_NORMAL
        ).pack(side="left", padx=5)

        tk.Label(
            matrix_size_frame,
            text="(2-4)",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_ITALIC
        ).pack(side="left", padx=5)

        # --- Опції модифікованого режиму (центровані) ---
        self.modified_options_frame = tk.Frame(left_panel, bg=BG_COLOR)

        tk.Label(
            self.modified_options_frame,
            text="Макс. довжина шуму:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left", padx=5)

        self.max_noise_var = tk.IntVar(value=1)
        tk.Spinbox(
            self.modified_options_frame,
            from_=0,
            to=3,
            textvariable=self.max_noise_var,
            width=5,
            font=FONT_NORMAL
        ).pack(side="left", padx=5)

        # --- Зашифрований текст ---
        tk.Label(
            left_panel,
            text="Зашифрований текст:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(pady=(20, 5))

        encrypted_text_frame = tk.Frame(left_panel, bg=BG_COLOR)
        encrypted_text_frame.pack(pady=5, padx=50)

        self.encrypted_text = tk.Text(
            encrypted_text_frame,
            width=45,
            height=7,
            font=FONT_NORMAL
        )
        self.encrypted_text.pack(side="left", fill="both", expand=True)

        encrypted_scroll = tk.Scrollbar(encrypted_text_frame, command=self.encrypted_text.yview)
        encrypted_scroll.pack(side="right", fill="y")
        self.encrypted_text.config(yscrollcommand=encrypted_scroll.set)

        tk.Button(
            left_panel,
            text="Завантажити з файлу",
            command=self.load_encrypted_text,
            bg=CELL_BG,
            fg="black"
        ).pack(pady=5)

        # --- Очікуваний текст (для порівняння) ---
        tk.Label(
            left_panel,
            text="Очікуваний текст (оригінал):",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(pady=(15, 5))

        expected_text_frame = tk.Frame(left_panel, bg=BG_COLOR)
        expected_text_frame.pack(pady=5, padx=50)

        self.expected_text = tk.Text(
            expected_text_frame,
            width=45,
            height=7,
            font=FONT_NORMAL
        )
        self.expected_text.pack(side="left", fill="both", expand=True)

        expected_scroll = tk.Scrollbar(expected_text_frame, command=self.expected_text.yview)
        expected_scroll.pack(side="right", fill="y")
        self.expected_text.config(yscrollcommand=expected_scroll.set)

        tk.Button(
            left_panel,
            text="Завантажити з файлу",
            command=self.load_expected_text,
            bg=CELL_BG,
            fg="black"
        ).pack(pady=5)

        # --- Кнопка старту/паузи (центрована) ---
        self.start_button = tk.Button(
            left_panel,
            text="Старт",
            command=self.toggle_brute_force,
            font=("Arial", 12, "bold"),
            bg=BUTTON_BG,
            fg=FG_COLOR,
            width=20,
            height=2
        )
        self.start_button.pack(pady=20)

        # ==================== ПРАВА ПАНЕЛЬ ====================
        right_panel = tk.Frame(main_container, bg=BG_COLOR)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # --- Лічильники спроб (зверху, центровані) ---
        counters_frame = tk.Frame(right_panel, bg=BG_COLOR)
        counters_frame.pack(pady=10)

        # Загальна кількість спроб (сірий колір)
        attempts_frame = tk.Frame(counters_frame, bg=BG_COLOR)
        attempts_frame.pack(pady=5)

        tk.Label(
            attempts_frame,
            text="Кількість спроб:",
            bg=BG_COLOR,
            fg="#808080",  # Сірий колір
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=5)

        self.attempts_var = tk.StringVar(value="0")
        tk.Label(
            attempts_frame,
            textvariable=self.attempts_var,
            bg=BG_COLOR,
            fg="#808080",  # Сірий колір
            font=("Arial", 14, "bold")
        ).pack(side="left")

        # Успішні спроби (зелений колір)
        successful_frame = tk.Frame(counters_frame, bg=BG_COLOR)
        successful_frame.pack(pady=5)

        tk.Label(
            successful_frame,
            text="Успішних (обернена матриця існує):",
            bg=BG_COLOR,
            fg="#00AA00",  # Зелений колір
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=5)

        self.successful_var = tk.StringVar(value="0")
        tk.Label(
            successful_frame,
            textvariable=self.successful_var,
            bg=BG_COLOR,
            fg="#00AA00",  # Зелений колір
            font=("Arial", 14, "bold")
        ).pack(side="left")

        # --- Статус ---
        self.status_var = tk.StringVar(value="Очікування...")
        tk.Label(
            right_panel,
            textvariable=self.status_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=FONT_ITALIC
        ).pack(pady=5)

        # --- Заголовок результатів ---
        tk.Label(
            right_panel,
            text="Найкращі результати:",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=("Arial", 12, "bold")
        ).pack(pady=(15, 10))

        # --- 5 контейнерів результатів ---
        self.result_containers = []
        for i in range(5):
            container = self.create_result_container(right_panel, i + 1)
            self.result_containers.append(container)

    def create_result_container(self, parent, number):
        """Створення контейнера для результату"""
        container_frame = tk.Frame(
            parent,
            bg=ACCENT_COLOR,
            relief="ridge",
            bd=2
        )
        container_frame.pack(pady=5, padx=20, fill="x")

        # Верхня частина: номер та точність
        header_frame = tk.Frame(container_frame, bg=ACCENT_COLOR)
        header_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            header_frame,
            text=f"#{number}",
            bg=ACCENT_COLOR,
            fg=FG_COLOR,
            font=FONT_BOLD
        ).pack(side="left")

        accuracy_var = tk.StringVar(value="Точність: ---%")
        accuracy_label = tk.Label(
            header_frame,
            textvariable=accuracy_var,
            bg=ACCENT_COLOR,
            fg="#808080",  # Початково сірий
            font=FONT_BOLD
        )
        accuracy_label.pack(side="left", padx=20)

        # Кнопка завантаження
        download_btn = tk.Button(
            header_frame,
            text="Зберегти",
            command=lambda n=number-1: self.save_result(n),
            bg=CELL_BG,
            fg="black",
            state="disabled"
        )
        download_btn.pack(side="right", padx=5)

        # Інформація про параметри
        info_var = tk.StringVar(value="Параметри: ---")
        info_label = tk.Label(
            container_frame,
            textvariable=info_var,
            bg=ACCENT_COLOR,
            fg=FG_COLOR,
            font=FONT_NORMAL
        )
        info_label.pack(fill="x", padx=10, pady=2)

        # Превью тексту
        preview_var = tk.StringVar(value="Текст: ---")
        preview_label = tk.Label(
            container_frame,
            textvariable=preview_var,
            bg=ACCENT_COLOR,
            fg=FG_COLOR,
            font=FONT_ITALIC,
            wraplength=400,
            justify="left"
        )
        preview_label.pack(fill="x", padx=10, pady=(2, 5))

        return {
            'frame': container_frame,
            'accuracy_var': accuracy_var,
            'accuracy_label': accuracy_label,
            'info_var': info_var,
            'preview_var': preview_var,
            'download_btn': download_btn
        }

    def get_accuracy_color(self, accuracy):
        """Отримати колір на основі точності (0% = червоний, 100% = зелений)"""
        # Нормалізуємо значення до 0-1
        ratio = max(0, min(100, accuracy)) / 100.0

        # Інтерполяція між червоним (#FF0000) та зеленим (#00FF00)
        red = int(255 * (1 - ratio))
        green = int(255 * ratio)

        return f"#{red:02X}{green:02X}00"

    def toggle_modified_options(self):
        """Перемикання видимості опцій модифікованого режиму"""
        if self.brute_mode.get() == 1:
            self.modified_options_frame.pack(pady=10, after=self.matrix_size_var.master)
        else:
            self.modified_options_frame.pack_forget()

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

    def load_encrypted_text(self):
        """Завантажити зашифрований текст"""
        text = load_text_file()
        if text:
            self.encrypted_text.delete("1.0", tk.END)
            self.encrypted_text.insert(tk.END, text)

    def load_expected_text(self):
        """Завантажити очікуваний текст"""
        text = load_text_file()
        if text:
            self.expected_text.delete("1.0", tk.END)
            self.expected_text.insert(tk.END, text)

    def toggle_brute_force(self):
        """Перемикання стану брутфорсу (старт/пауза/продовжити)"""
        if not self.is_running:
            # Старт
            self.start_brute_force()
        elif self.is_paused:
            # Продовжити
            self.resume_brute_force()
        else:
            # Пауза
            self.pause_brute_force()

    def start_brute_force(self):
        """Запуск брутфорсу"""
        # Валідація
        encrypted = self.encrypted_text.get("1.0", tk.END).strip()
        expected = self.expected_text.get("1.0", tk.END).strip()

        if not encrypted:
            messagebox.showerror("Помилка", "Введіть зашифрований текст!")
            return

        if not expected:
            messagebox.showerror("Помилка", "Введіть очікуваний текст!")
            return

        # Скидаємо стан
        self.is_running = True
        self.is_paused = False
        self.attempts_count = 0
        self.successful_attempts = 0
        self.results = []
        self.brute_threads = []

        # Оновлюємо UI
        self.start_button.config(text="Пауза")
        self.status_var.set("Виконується брутфорс (2 потоки)...")
        self.clear_results()

        # Запускаємо два потоки - один з початку, інший з кінця
        thread1 = threading.Thread(target=self.brute_force_worker, args=(False,), daemon=True)
        thread2 = threading.Thread(target=self.brute_force_worker, args=(True,), daemon=True)

        self.brute_threads = [thread1, thread2]
        thread1.start()
        thread2.start()

        # Потік для моніторингу завершення
        monitor_thread = threading.Thread(target=self.monitor_threads, daemon=True)
        monitor_thread.start()

    def monitor_threads(self):
        """Моніторинг завершення потоків"""
        for thread in self.brute_threads:
            thread.join()
        self.window.after(0, self.stop_brute_force)

    def pause_brute_force(self):
        """Призупинення брутфорсу"""
        self.is_paused = True
        self.start_button.config(text="Продовжити")
        self.status_var.set("Призупинено")

    def resume_brute_force(self):
        """Продовження брутфорсу"""
        self.is_paused = False
        self.start_button.config(text="Пауза")
        self.status_var.set("Виконується брутфорс (2 потоки)...")

    def stop_brute_force(self):
        """Зупинка брутфорсу"""
        self.is_running = False
        self.is_paused = False
        self.start_button.config(text="Старт")
        self.status_var.set("Завершено")

    def clear_results(self):
        """Очищення контейнерів результатів"""
        for container in self.result_containers:
            container['accuracy_var'].set("Точність: ---%")
            container['accuracy_label'].config(fg="#808080")
            container['info_var'].set("Параметри: ---")
            container['preview_var'].set("Текст: ---")
            container['download_btn'].config(state="disabled")

    def calculate_accuracy(self, decrypted, expected):
        """
        Обчислення точності розшифрування.
        Використовується формула схожості рядків.
        """
        if not decrypted or not expected:
            return 0.0

        # Простіша метрика: відсоток співпадаючих символів на тих самих позиціях
        min_len = min(len(decrypted), len(expected))
        if min_len == 0:
            return 0.0

        matches = sum(1 for i in range(min_len) if decrypted[i] == expected[i])

        # Штраф за різницю в довжині
        length_penalty = 1.0 - abs(len(decrypted) - len(expected)) / max(len(decrypted), len(expected))

        accuracy = (matches / min_len) * length_penalty * 100

        return round(accuracy, 2)

    def is_zero_matrix(self, matrix):
        """Перевірка чи матриця складається тільки з нулів"""
        for row in matrix:
            for val in row:
                if val != 0:
                    return False
        return True

    def is_valid_matrix(self, matrix, mod):
        """Перевірка чи матриця має обернену за модулем"""
        try:
            det = determinant_int(matrix)
            det_mod = det % mod

            if det_mod == 0:
                return False

            # Перевіряємо чи є обернений елемент
            for x in range(1, mod):
                if (det_mod * x) % mod == 1:
                    return True

            return False
        except:
            return False

    def brute_force_worker(self, reverse=False):
        """Робочий процес брутфорсу"""
        encrypted = self.encrypted_text.get("1.0", tk.END).strip()
        expected = self.expected_text.get("1.0", tk.END).strip()
        matrix_size = self.matrix_size_var.get()
        mod = len(self.alphabet)

        if self.brute_mode.get() == 0:
            # Стандартний режим
            self.brute_force_standard(encrypted, expected, matrix_size, mod, reverse)
        else:
            # Модифікований режим
            max_noise = self.max_noise_var.get()
            self.brute_force_modified(encrypted, expected, matrix_size, mod, max_noise, reverse)

    def brute_force_standard(self, encrypted, expected, matrix_size, mod, reverse=False):
        """Брутфорс стандартного режиму"""
        value_range = min(mod, 10)  # Обмежуємо до 10 значень для швидкості
        total_elements = matrix_size * matrix_size

        # Генеруємо всі можливі комбінації
        all_combinations = list(itertools.product(range(value_range), repeat=total_elements))

        if reverse:
            all_combinations = list(reversed(all_combinations))

        for values in all_combinations:
            # Перевіряємо чи потрібно зупинитися
            if not self.is_running:
                return

            # Очікуємо якщо на паузі
            while self.is_paused and self.is_running:
                time.sleep(0.1)

            # Формуємо матрицю
            matrix = [list(values[i*matrix_size:(i+1)*matrix_size]) for i in range(matrix_size)]

            # Пропускаємо матриці з нулями
            if self.is_zero_matrix(matrix):
                with self.lock:
                    self.attempts_count += 1
                continue

            # Перевіряємо валідність матриці
            if not self.is_valid_matrix(matrix, mod):
                with self.lock:
                    self.attempts_count += 1
                    if self.attempts_count % 100 == 0:
                        self.window.after(0, self.update_counters)
                continue

            # Успішна матриця (має обернену)
            with self.lock:
                self.successful_attempts += 1

            # Спробуємо розшифрувати
            try:
                ciphertext_numbers = text_to_numbers(encrypted, self.alphabet)
                dec_numbers = hill_decrypt_standard(ciphertext_numbers, matrix, self.alphabet)
                decrypted = numbers_to_text(dec_numbers, self.alphabet)

                # Обчислюємо точність
                accuracy = self.calculate_accuracy(decrypted, expected)

                # Додаємо до результатів якщо точність > 0
                if accuracy > 0:
                    self.add_result(accuracy, matrix, None, 0, decrypted)

            except Exception:
                pass

            with self.lock:
                self.attempts_count += 1

                # Оновлюємо лічильник кожні 100 спроб
                if self.attempts_count % 100 == 0:
                    self.window.after(0, self.update_counters)

    def brute_force_modified(self, encrypted, expected, matrix_size, mod, max_noise, reverse=False):
        """Брутфорс модифікованого режиму"""
        value_range = min(mod, 8)  # Менший діапазон для модифікованого режиму
        total_elements = matrix_size * matrix_size

        # Генеруємо комбінації
        all_combinations = list(itertools.product(range(value_range), repeat=total_elements))

        if reverse:
            all_combinations = list(reversed(all_combinations))

        # Перебираємо різні довжини шуму
        noise_range = range(max_noise + 1) if not reverse else reversed(range(max_noise + 1))

        for noise_length in noise_range:
            if noise_length >= matrix_size:
                continue

            # Генеруємо прості підстановки (циклічний зсув)
            shift_range = range(mod) if not reverse else reversed(range(mod))

            for shift in shift_range:
                substitution = [(i + shift) % mod for i in range(mod)]

                # Генеруємо матриці
                for values in all_combinations:
                    if not self.is_running:
                        return

                    while self.is_paused and self.is_running:
                        time.sleep(0.1)

                    matrix = [list(values[i*matrix_size:(i+1)*matrix_size]) for i in range(matrix_size)]

                    # Пропускаємо матриці з нулями
                    if self.is_zero_matrix(matrix):
                        with self.lock:
                            self.attempts_count += 1
                        continue

                    if not self.is_valid_matrix(matrix, mod):
                        with self.lock:
                            self.attempts_count += 1
                            if self.attempts_count % 100 == 0:
                                self.window.after(0, self.update_counters)
                        continue

                    # Успішна матриця
                    with self.lock:
                        self.successful_attempts += 1

                    try:
                        decrypted = hill_decrypt_modified(
                            encrypted,
                            matrix,
                            self.alphabet,
                            substitution,
                            noise_length
                        )

                        accuracy = self.calculate_accuracy(decrypted, expected)

                        if accuracy > 0:
                            self.add_result(accuracy, matrix, substitution, noise_length, decrypted)

                    except Exception:
                        pass

                    with self.lock:
                        self.attempts_count += 1

                        if self.attempts_count % 100 == 0:
                            self.window.after(0, self.update_counters)

    def update_counters(self):
        """Оновлення лічильників у UI"""
        self.attempts_var.set(str(self.attempts_count))
        self.successful_var.set(str(self.successful_attempts))

    def add_result(self, accuracy, matrix, substitution, noise_length, decrypted_text):
        """Додавання результату до списку найкращих"""
        result = {
            'accuracy': accuracy,
            'matrix': [row[:] for row in matrix],  # Копіюємо матрицю
            'substitution': substitution[:] if substitution else None,
            'noise_length': noise_length,
            'decrypted_text': decrypted_text
        }

        with self.lock:
            # Перевіряємо чи такий результат вже є
            for existing in self.results:
                if existing['matrix'] == result['matrix'] and \
                   existing['substitution'] == result['substitution'] and \
                   existing['noise_length'] == result['noise_length']:
                    return  # Пропускаємо дублікати

            # Додаємо та сортуємо за точністю
            self.results.append(result)
            self.results.sort(key=lambda x: x['accuracy'], reverse=True)

            # Залишаємо тільки топ-5
            self.results = self.results[:5]

        # Оновлюємо UI
        self.window.after(0, self.update_results_ui)

    def update_results_ui(self):
        """Оновлення UI з результатами"""
        for i, container in enumerate(self.result_containers):
            if i < len(self.results):
                result = self.results[i]

                accuracy = result['accuracy']
                container['accuracy_var'].set(f"Точність: {accuracy}%")

                # Встановлюємо колір на основі точності
                color = self.get_accuracy_color(accuracy)
                container['accuracy_label'].config(fg=color)

                # Параметри
                matrix_str = f"Матриця {len(result['matrix'])}x{len(result['matrix'])}"
                if result['substitution']:
                    params = f"{matrix_str}, Шум: {result['noise_length']}, Зсув підстановки"
                else:
                    params = matrix_str
                container['info_var'].set(f"Параметри: {params}")

                # Превью тексту
                preview = result['decrypted_text'][:100]
                if len(result['decrypted_text']) > 100:
                    preview += "..."
                container['preview_var'].set(f"Текст: {preview}")

                container['download_btn'].config(state="normal")
            else:
                container['accuracy_var'].set("Точність: ---%")
                container['accuracy_label'].config(fg="#808080")
                container['info_var'].set("Параметри: ---")
                container['preview_var'].set("Текст: ---")
                container['download_btn'].config(state="disabled")

    def save_result(self, index):
        """Збереження результату"""
        if index >= len(self.results):
            return

        result = self.results[index]

        # Формуємо текст для збереження
        output = f"=== Результат брутфорсу ===\n\n"
        output += f"Точність: {result['accuracy']}%\n\n"
        output += f"Матриця:\n"
        for row in result['matrix']:
            output += f"  {row}\n"
        output += f"\n"

        if result['substitution']:
            output += f"Довжина шуму: {result['noise_length']}\n"
            output += f"Підстановка (перші 20): {result['substitution'][:20]}...\n\n"

        output += f"Розшифрований текст:\n{result['decrypted_text']}\n"

        # Зберігаємо
        success = save_file(
            output,
            f"brute_force_result_{index + 1}.txt",
            "Зберегти результат брутфорсу"
        )

        if success:
            messagebox.showinfo("Успіх", "Результат збережено!")
