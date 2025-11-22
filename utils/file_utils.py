"""
Утиліти для роботи з файлами
"""

import os
from tkinter import filedialog, messagebox


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