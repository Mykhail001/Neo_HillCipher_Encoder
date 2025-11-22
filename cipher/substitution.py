"""
Модуль для роботи з підстановками
"""

import secrets


def generate_random_substitution(size):
    """
    Генерує випадкову підстановку заданого розміру

    Args:
        size: Розмір підстановки

    Returns:
        list: Випадкова підстановка
    """
    numbers = list(range(size))

    # Алгоритм Fisher-Yates для безпечного перемішування
    for i in reversed(range(1, size)):
        j = secrets.randbelow(i + 1)
        numbers[i], numbers[j] = numbers[j], numbers[i]

    return numbers


def create_shift_substitution(size, shift=1):
    """
    Створює зміщену підстановку (циклічний зсув)

    Args:
        size: Розмір підстановки
        shift: Величина зсуву (за замовчуванням 1)

    Returns:
        list: Зміщена підстановка
    """
    shift = shift % size  # Нормалізуємо зсув
    return [(i + shift) % size for i in range(size)]


def create_reverse_substitution(size):
    """
    Створює реверсну підстановку (0->n-1, 1->n-2, ...)

    Args:
        size: Розмір підстановки

    Returns:
        list: Реверсна підстановка
    """
    return list(reversed(range(size)))


def invert_substitution(substitution):
    """
    Обчислює обернену підстановку

    Args:
        substitution: Вихідна підстановка

    Returns:
        list: Обернена підстановка
    """
    n = len(substitution)
    inverse = [0] * n

    for i, val in enumerate(substitution):
        inverse[val % n] = i

    return inverse


def validate_substitution(substitution, expected_size=None):
    """
    Перевіряє коректність підстановки

    Args:
        substitution: Підстановка для перевірки
        expected_size: Очікуваний розмір (опціонально)

    Returns:
        tuple: (is_valid, error_message)
    """
    if not substitution:
        return False, "Підстановка порожня"

    if not isinstance(substitution, (list, tuple)):
        return False, "Підстановка має бути списком або кортежем"

    size = len(substitution)

    if expected_size is not None and size != expected_size:
        return False, f"Розмір підстановки ({size}) не відповідає очікуваному ({expected_size})"

    # Перевірка на дублікати
    if len(set(substitution)) != size:
        return False, "Підстановка містить дублікати"

    # Перевірка діапазону значень
    for i, val in enumerate(substitution):
        if not isinstance(val, int):
            return False, f"Елемент {i} не є цілим числом: {val}"
        if val < 0 or val >= size:
            return False, f"Значення {val} виходить за межі діапазону [0, {size - 1}]"

    return True, "Підстановка коректна"


def apply_substitution(data, substitution):
    """
    Застосовує підстановку до даних

    Args:
        data: Список чисел для підстановки
        substitution: Підстановка

    Returns:
        list: Дані після підстановки
    """
    return [substitution[x % len(substitution)] for x in data]


def apply_substitution_multiple(data, substitution, times=1):
    """
    Застосовує підстановку кілька разів

    Args:
        data: Список чисел для підстановки
        substitution: Підстановка
        times: Кількість застосувань

    Returns:
        list: Дані після багаторазової підстановки
    """
    result = data.copy()
    for _ in range(times):
        result = apply_substitution(result, substitution)
    return result


def compose_substitutions(subst1, subst2):
    """
    Композиція двох підстановок (subst1 ∘ subst2)

    Args:
        subst1: Перша підстановка
        subst2: Друга підстановка

    Returns:
        list: Композиція підстановок
    """
    if len(subst1) != len(subst2):
        raise ValueError("Підстановки мають бути однакового розміру")

    return [subst1[subst2[i]] for i in range(len(subst1))]


def substitution_order(substitution):
    """
    Обчислює порядок підстановки (мінімальна кількість застосувань для повернення до початкового стану)

    Args:
        substitution: Підстановка

    Returns:
        int: Порядок підстановки
    """
    n = len(substitution)
    visited = [False] * n
    lcm = 1

    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    def lcm_func(a, b):
        return abs(a * b) // gcd(a, b)

    # Знаходимо всі цикли
    for i in range(n):
        if not visited[i]:
            cycle_length = 0
            current = i

            while not visited[current]:
                visited[current] = True
                current = substitution[current]
                cycle_length += 1

            lcm = lcm_func(lcm, cycle_length)

    return lcm


def substitution_to_string(substitution):
    """
    Конвертує підстановку в рядок для збереження

    Args:
        substitution: Підстановка

    Returns:
        str: Рядкове представлення
    """
    return " ".join(str(x) for x in substitution)


def string_to_substitution(string):
    """
    Конвертує рядок в підстановку

    Args:
        string: Рядкове представлення

    Returns:
        list: Підстановка
    """
    try:
        return [int(x) for x in string.split()]
    except ValueError:
        raise ValueError("Некоректний формат підстановки")


# Шаблони підстановок
SUBSTITUTION_TEMPLATES = {
    "shift_1": lambda size: create_shift_substitution(size, 1),
    "shift_-1": lambda size: create_shift_substitution(size, -1),
    "reverse": lambda size: create_reverse_substitution(size),
    "identity": lambda size: list(range(size)),
    "random": lambda size: generate_random_substitution(size)
}


def get_template_substitution(template_name, size):
    """
    Отримати підстановку за шаблоном

    Args:
        template_name: Назва шаблону
        size: Розмір підстановки

    Returns:
        list: Підстановка за шаблоном
    """
    if template_name not in SUBSTITUTION_TEMPLATES:
        raise ValueError(f"Невідомий шаблон: {template_name}")

    return SUBSTITUTION_TEMPLATES[template_name](size)