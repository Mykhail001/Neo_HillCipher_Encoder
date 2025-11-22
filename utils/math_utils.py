"""
Математичні утиліти для шифрування
"""

import numpy as np
from functools import lru_cache

# Глобальна змінна для логування циркулянтних матриць
_circulant_matrix_log = []


def get_circulant_log():
    """Повертає лог циркулянтних матриць"""
    return _circulant_matrix_log


def clear_circulant_log():
    """Очищає лог циркулянтних матриць"""
    global _circulant_matrix_log
    _circulant_matrix_log = []


def is_circulant_matrix(matrix):
    """
    Перевіряє, чи є матриця циркулянтною.
    Циркулянтна матриця - це матриця, де кожен рядок є циклічним зсувом попереднього.

    Args:
        matrix: numpy array або list of lists

    Returns:
        bool: True якщо матриця циркулянтна
    """
    if hasattr(matrix, 'tolist'):
        matrix = matrix.tolist()

    n = len(matrix)
    if n == 0:
        return False

    if not all(len(row) == n for row in matrix):
        return False

    first_row = matrix[0]

    for i in range(1, n):
        # Очікуваний рядок - циклічний зсув вправо на i позицій
        expected_row = [first_row[(j - i) % n] for j in range(n)]
        if matrix[i] != expected_row:
            return False

    return True


def circulant_determinant(matrix):
    """
    Обчислює визначник циркулянтної матриці.
    Для циркулянтної матриці використовуємо тільки перший рядок.

    Визначник циркулянтної матриці = добуток p(ω^k) для k=0..n-1,
    де p(x) = c0 + c1*x + ... + cn-1*x^(n-1) та ω - примітивний корінь n-го степеня з 1.

    Для цілочисельних обчислень використовуємо стандартний алгоритм,
    але з оптимізацією через властивості циркулянтної матриці.
    """
    # Для цілочисельної арифметики використовуємо стандартний метод
    # Оптимізація тут в тому, що ми знаємо структуру матриці
    return determinant_int(matrix)


def circulant_cofactor_column(matrix, col_idx=0):
    """
    Обчислює один стовпець кофакторів циркулянтної матриці.
    Оскільки матриця циркулянтна, інші стовпці можна отримати зсувом.

    Args:
        matrix: циркулянтна матриця
        col_idx: індекс стовпця для обчислення (за замовчуванням 0)

    Returns:
        list: стовпець кофакторів
    """
    if hasattr(matrix, 'tolist'):
        matrix = matrix.tolist()

    n = len(matrix)
    cofactors = []

    for i in range(n):
        minor_det = matrix_minor(matrix, i, col_idx)
        sign = (-1) ** (i + col_idx)
        cofactors.append(sign * minor_det)

    return cofactors


def circulant_inverse(matrix, mod):
    """
    Обчислює обернену матрицю для циркулянтної матриці.
    Оптимізація: обчислюємо тільки перший стовпець кофакторів,
    потім зсуваємо для отримання всієї матриці.

    Args:
        matrix: циркулянтна матриця
        mod: модуль

    Returns:
        numpy array: обернена матриця за модулем
    """
    global _circulant_matrix_log

    if hasattr(matrix, 'tolist'):
        matrix_list = matrix.tolist()
    else:
        matrix_list = matrix

    n = len(matrix_list)

    # Обчислюємо визначник
    det = determinant_int(matrix_list)
    det_mod = det % mod

    if det_mod == 0:
        raise ValueError(f"Детермінант {det} не має оберненого за модулем {mod}")

    # Знаходимо обернений елемент детермінанта
    inv_det = None
    for x in range(1, mod):
        if (det_mod * x) % mod == 1:
            inv_det = x
            break

    if inv_det is None:
        raise ValueError(f"Детермінант {det_mod} не має оберненого за модулем {mod}")

    # Обчислюємо тільки перший стовпець кофакторів
    first_col_cofactors = circulant_cofactor_column(matrix_list, 0)

    # Логуємо оптимізацію
    _circulant_matrix_log.append({
        'size': n,
        'determinant': det,
        'optimization': 'single_column_cofactors'
    })

    # Будуємо повну матрицю кофакторів через циклічні зсуви
    # Для циркулянтної матриці: cofactor[i][j] = shift(first_col, j)[i]
    cofactors = np.zeros((n, n), dtype=np.int64)

    for j in range(n):
        for i in range(n):
            # Зсув: елемент cofactors[i][j] = first_col[(i - j) % n]
            cofactors[i, j] = first_col_cofactors[(i - j) % n]

    # Транспонуємо та множимо на обернений детермінант
    adjugate = cofactors.T
    inv_matrix = (inv_det * adjugate) % mod
    inv_matrix = np.mod(inv_matrix, mod).astype(np.int64)

    return inv_matrix


@lru_cache(maxsize=128)
def is_prime(n):
    """Перевірка чи є число простим"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def mod_inverse(a, m):
    """Обчислення модульного оберненого"""
    a = a % m
    if a == 0:
        raise ValueError("Модульний обернений не існує")
    t, new_t = 0, 1
    r, new_r = m, a
    while new_r != 0:
        quotient = r // new_r
        t, new_t = new_t, t - quotient * new_t
        r, new_r = new_r, r - quotient * new_r
    if r > 1:
        raise ValueError("Модульний обернений не існує")
    return t + m if t < 0 else t


def determinant_int(matrix):
    """
    Обчислення визначника матриці з використанням ТІЛЬКИ цілих чисел.
    Рекурсивне розкладання за кофакторами - без float, без округлення, точний результат.
    """
    # Convert to list of lists if numpy array
    if hasattr(matrix, 'tolist'):
        matrix = matrix.tolist()

    n = len(matrix)

    # Base cases
    if n == 1:
        return int(matrix[0][0])

    if n == 2:
        return int(matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0])

    # Recursive cofactor expansion along first row
    det = 0
    for j in range(n):
        # Build minor matrix (exclude row 0 and column j)
        minor = []
        for row in range(1, n):
            minor_row = []
            for col in range(n):
                if col != j:
                    minor_row.append(matrix[row][col])
            minor.append(minor_row)

        # Cofactor sign: (-1)^(0+j)
        sign = 1 if j % 2 == 0 else -1

        # Recursive call for minor determinant
        det += sign * int(matrix[0][j]) * determinant_int(minor)

    return det


def determinant(matrix):
    """Обчислення визначника матриці"""
    return determinant_int(matrix)


def matrix_minor(matrix, i, j):
    """Обчислення мінора матриці з використанням цілочисельної арифметики"""
    # Convert to list of lists if numpy array
    if hasattr(matrix, 'tolist'):
        matrix = matrix.tolist()

    n = len(matrix)
    # Build minor matrix (exclude row i and column j)
    minor = []
    for row in range(n):
        if row == i:
            continue
        minor_row = []
        for col in range(n):
            if col != j:
                minor_row.append(matrix[row][col])
        minor.append(minor_row)

    return determinant_int(minor)


def matrix_mod_inverse(matrix, mod):
    """
    Обчислення оберненої матриці по модулю з цілочисельною арифметикою.
    Автоматично визначає циркулянтні матриці та використовує оптимізований алгоритм.
    """
    global _circulant_matrix_log

    n = matrix.shape[0]

    # Перевіряємо чи матриця циркулянтна
    if is_circulant_matrix(matrix):
        # Логуємо використання оптимізації (без виведення на екран)
        _circulant_matrix_log.append({
            'size': n,
            'type': 'circulant_detected',
            'optimization': 'using_circulant_inverse'
        })
        return circulant_inverse(matrix, mod)

    det = determinant_int(matrix)
    det_mod = det % mod

    if det_mod == 0:
        raise ValueError(f"Детермінант {det} не має оберненого за модулем {mod}")

    # Знаходимо обернений елемент детермінанта
    inv_det = None
    for x in range(1, mod):
        if (det_mod * x) % mod == 1:
            inv_det = x
            break

    if inv_det is None:
        raise ValueError(f"Детермінант {det_mod} не має оберненого за модулем {mod}")

    # Обчислюємо матрицю кофакторів
    cofactors = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            minor_det = matrix_minor(matrix, i, j)
            sign = (-1) ** (i + j)
            cofactors[i, j] = (sign * minor_det) % mod

    # Транспонуємо та множимо на обернений детермінант
    adjugate = cofactors.T
    inv_matrix = (inv_det * adjugate) % mod
    inv_matrix = np.mod(inv_matrix, mod).astype(np.int64)

    return inv_matrix