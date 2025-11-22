"""
Математичні утиліти для шифрування
"""

import numpy as np
from functools import lru_cache


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
    Обчислення визначника матриці з використанням ТІЛЬКИ цілочисельної арифметики.
    Використовує рекурсивне розкладання по першому рядку.
    Це критично для великих матриць (9x9+) де float втрачає точність.
    """
    matrix = [[int(x) for x in row] for row in matrix]
    n = len(matrix)

    if n == 1:
        return matrix[0][0]

    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

    det = 0
    for j in range(n):
        # Створюємо мінор (видаляємо рядок 0 і стовпець j)
        minor = []
        for i in range(1, n):
            row = []
            for k in range(n):
                if k != j:
                    row.append(matrix[i][k])
            minor.append(row)

        # Знак: (-1)^(0+j)
        sign = 1 if j % 2 == 0 else -1
        det += sign * matrix[0][j] * determinant_int(minor)

    return det


def determinant(matrix):
    """Обчислення визначника матриці (цілочисельна версія)"""
    return determinant_int(matrix)


def matrix_minor_int(matrix, i, j):
    """
    Обчислення мінора матриці (визначник без рядка i та стовпця j)
    з використанням цілочисельної арифметики.
    """
    matrix = [[int(x) for x in row] for row in matrix]
    n = len(matrix)

    # Створюємо підматрицю без рядка i та стовпця j
    minor = []
    for row_idx in range(n):
        if row_idx == i:
            continue
        row = []
        for col_idx in range(n):
            if col_idx == j:
                continue
            row.append(matrix[row_idx][col_idx])
        minor.append(row)

    return determinant_int(minor)


def matrix_minor(matrix, i, j):
    """Обчислення мінора матриці"""
    return matrix_minor_int(matrix, i, j)


def matrix_mod_inverse(matrix, mod):
    """
    Обчислення оберненої матриці по модулю.
    Використовує цілочисельну арифметику для уникнення помилок округлення.
    """
    # Конвертуємо в список списків для цілочисельних операцій
    if isinstance(matrix, np.ndarray):
        matrix_list = [[int(x) for x in row] for row in matrix.tolist()]
    else:
        matrix_list = [[int(x) for x in row] for row in matrix]

    n = len(matrix_list)

    # Обчислюємо визначник цілочисельно
    det = determinant_int(matrix_list)
    det_mod = det % mod

    if det_mod == 0:
        raise ValueError(f"Детермінант {det} не має оберненого за модулем {mod}")

    # Знаходимо обернений елемент детермінанта
    try:
        inv_det = mod_inverse(det_mod, mod)
    except ValueError:
        raise ValueError(f"Детермінант {det_mod} не має оберненого за модулем {mod}")

    # Обчислюємо матрицю кофакторів (цілочисельно)
    cofactors = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            minor_det = matrix_minor_int(matrix_list, i, j)
            sign = 1 if (i + j) % 2 == 0 else -1
            cofactors[i][j] = (sign * minor_det) % mod

    # Транспонуємо (adjugate = cofactors^T)
    adjugate = [[cofactors[j][i] for j in range(n)] for i in range(n)]

    # Множимо на обернений детермінант і беремо по модулю
    inv_matrix = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            inv_matrix[i, j] = (inv_det * adjugate[i][j]) % mod

    return inv_matrix