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


def determinant(matrix):
    """Обчислення визначника матриці"""
    return round(np.linalg.det(np.array(matrix)))


def matrix_minor(matrix, i, j):
    """Обчислення мінора матриці"""
    minor = np.delete(np.delete(matrix, i, axis=0), j, axis=1)
    return int(round(np.linalg.det(minor)))


def matrix_mod_inverse(matrix, mod):
    """Обчислення оберненої матриці по модулю"""
    n = matrix.shape[0]

    det = int(round(np.linalg.det(matrix)))
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