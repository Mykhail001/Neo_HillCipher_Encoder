"""
Утиліти для роботи з файлами
"""

import os
import base64
from tkinter import filedialog, messagebox

# Стандартні символи Base64
BASE64_CHARS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')

# Символ для padding за замовчуванням
DEFAULT_PADDING_SYMBOL = "."


def validate_alphabet_for_base64(alphabet, padding_symbol, include_ext_marker=True):
    """
    Перевіряє, чи алфавіт містить всі необхідні символи для Base64 шифрування файлів

    Args:
        alphabet: Рядок з символами алфавіту
        padding_symbol: Символ для padding
        include_ext_marker: Чи включати символи маркера EXT (E, X, T, :, .)

    Returns:
        tuple: (is_valid, missing_chars)
    """
    alphabet_set = set(alphabet)

    # Необхідні символи: Base64 + padding
    required_chars = BASE64_CHARS.copy()
    required_chars.add(padding_symbol)

    # Якщо використовуємо маркер EXT, потрібні додаткові символи
    if include_ext_marker:
        required_chars.add(':')
        required_chars.add('.')

    missing_chars = required_chars - alphabet_set
    return len(missing_chars) == 0, missing_chars


def get_all_chars_in_text(text):
    """
    Повертає множину всіх унікальних символів у тексті
    """
    return set(text)


def validate_text_for_alphabet(text, alphabet):
    """
    Перевіряє, чи всі символи тексту є в алфавіті

    Returns:
        tuple: (is_valid, missing_chars)
    """
    alphabet_set = set(alphabet)
    text_chars = set(text)
    missing_chars = text_chars - alphabet_set
    return len(missing_chars) == 0, missing_chars


def file_to_base64_with_marker(file_path):
    """
    Конвертує файл в Base64 з маркером оригінального формату

    Returns:
        tuple: (base64_string, original_extension)
    """
    with open(file_path, "rb") as f:
        data = f.read()

    original_extension = os.path.splitext(file_path)[1]
    encoded_bytes = base64.b64encode(data)
    encoded_str = encoded_bytes.decode('ascii')

    # Формат: EXT:.ext:base64data
    if original_extension:
        marker = f"EXT:{original_extension}:"
    else:
        marker = ""

    return marker + encoded_str, original_extension


def add_padding_for_matrix(text, matrix_size, padding_char=PADDING_SYMBOL):
    """
    Додає padding символи до тексту, щоб довжина була кратна розміру матриці

    Returns:
        tuple: (padded_text, padding_count)
    """
    current_length = len(text)
    remainder = current_length % matrix_size

    if remainder == 0:
        return text, 0

    padding_count = matrix_size - remainder
    return text + (padding_char * padding_count), padding_count


def remove_padding(text, padding_char=PADDING_SYMBOL):
    """
    Видаляє padding символи з кінця тексту

    Returns:
        tuple: (clean_text, removed_count)
    """
    original_length = len(text)
    clean_text = text.rstrip(padding_char)
    removed_count = original_length - len(clean_text)
    return clean_text, removed_count


def base64_to_file(base64_text, output_dir, base_filename):
    """
    Конвертує Base64 текст назад у файл

    Returns:
        tuple: (success, output_path or error_message)
    """
    try:
        original_extension = ""

        # Перевіряємо чи є маркер з розширенням
        if base64_text.startswith("EXT:"):
            first_colon = base64_text.index(":")
            second_colon = base64_text.index(":", first_colon + 1)
            original_extension = base64_text[first_colon + 1:second_colon]
            base64_text = base64_text[second_colon + 1:]

        # Декодуємо Base64
        decoded_bytes = base64.b64decode(base64_text)

        # Формуємо шлях виходу
        if original_extension:
            output_path = os.path.join(output_dir, f"{base_filename}_restored{original_extension}")
        else:
            output_path = os.path.join(output_dir, f"{base_filename}_restored.bin")

        with open(output_path, "wb") as f:
            f.write(decoded_bytes)

        return True, output_path

    except Exception as e:
        return False, str(e)


def load_alphabet_file():
    """Завантаження алфавіту з файлу"""
    fpath = filedialog.askopenfilename(
        title="Відкрити алфавіт",
        filetypes=[("Text Files", "*.txt")]
    )
    if not fpath:
        return None

    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            messagebox.showerror("Помилка", "Файл порожній!")
            return None

        name = os.path.splitext(os.path.basename(fpath))[0]
        return content, name
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{e}")
        return None


def load_matrix_file():
    """Завантаження матриці з файлу"""
    fpath = filedialog.askopenfilename(
        title="Відкрити матрицю",
        filetypes=[("Text Files", "*.txt")]
    )
    if not fpath:
        return None, None

    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            messagebox.showerror("Помилка", "Файл порожній!")
            return None, None

        rows = content.splitlines()
        matrix_data = []
        for row in rows:
            parts = row.split(',')
            row_data = [int(part.strip()) for part in parts if part.strip()]
            if row_data:
                matrix_data.append(row_data)

        n = len(matrix_data)
        if not all(len(r) == n for r in matrix_data):
            messagebox.showerror("Помилка", "Матриця повинна бути квадратною!")
            return None, None

        name = os.path.splitext(os.path.basename(fpath))[0]
        return matrix_data, name
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося завантажити матрицю:\n{e}")
        return None, None


def load_substitution_file():
    """Завантаження підстановки з файлу"""
    fpath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not fpath:
        return None, None

    try:
        with open(fpath, "r", encoding="utf-8") as f:
            data = f.read().strip()

        if not data:
            messagebox.showerror("Помилка", "Файл підстановки порожній!")
            return None, None

        parts = data.split()
        mapping = [int(x) for x in parts]

        if len(mapping) != len(set(mapping)):
            messagebox.showerror("Помилка", "Підстановка містить дублікати!")
            return None, None

        name = os.path.splitext(os.path.basename(fpath))[0]
        return mapping, name
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося завантажити підстановку:\n{e}")
        return None, None


def load_text_file():
    """Завантаження текстового файлу"""
    fpath = filedialog.askopenfilename(
        title="Відкрити текстовий файл",
        filetypes=[("Text Files", "*.txt")]
    )
    if not fpath:
        return None

    try:
        with open(fpath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{e}")
        return None


def save_file(content, default_name, title="Зберегти файл"):
    """Збереження файлу"""
    file_path = filedialog.asksaveasfilename(
        initialfile=default_name,
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        title=title
    )

    if not file_path:
        return False

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Успіх", f"Файл збережено:\n{file_path}")
        return True
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося зберегти файл:\n{e}")
        return False