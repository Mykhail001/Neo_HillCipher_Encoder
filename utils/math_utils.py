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
    """Обчислення оберненої матриці по модулю з цілочисельною арифметикою"""
    n = matrix.shape[0]

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