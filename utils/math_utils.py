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


def circulant_cofactor_column(matrix, col_idx=0, show_progress=False):
    """
    Обчислює один стовпець кофакторів циркулянтної матриці.
    Оскільки матриця циркулянтна, інші стовпці можна отримати зсувом.

    Args:
        matrix: циркулянтна матриця
        col_idx: індекс стовпця для обчислення (за замовчуванням 0)
        show_progress: якщо True, виводить прогрес

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
        if show_progress:
            print(f"    Cofactor {i + 1}/{n}")

    return cofactors


def circulant_inverse(matrix, mod, show_progress=True):
    """
    Обчислює обернену матрицю для циркулянтної матриці.
    Оптимізація: обчислюємо тільки перший стовпець кофакторів,
    потім зсуваємо для отримання всієї матриці.

    Args:
        matrix: циркулянтна матриця
        mod: модуль
        show_progress: якщо True, виводить прогрес у консоль для великих матриць

    Returns:
        numpy array: обернена матриця за модулем
    """
    global _circulant_matrix_log

    if hasattr(matrix, 'tolist'):
        matrix_list = matrix.tolist()
    else:
        matrix_list = matrix

    n = len(matrix_list)
    show_log = show_progress and n >= 8

    if show_log:
        print(f"  Step 1/3: Computing determinant...")

    # Обчислюємо визначник
    det = determinant_int(matrix_list, show_progress=show_log)
    det_mod = det % mod

    if det_mod == 0:
        raise ValueError(f"Детермінант {det} не має оберненого за модулем {mod}")

    if show_log:
        print(f"  Step 2/3: Determinant = {det} (mod {mod} = {det_mod})")

    # Знаходимо обернений елемент детермінанта
    inv_det = None
    for x in range(1, mod):
        if (det_mod * x) % mod == 1:
            inv_det = x
            break

    if inv_det is None:
        raise ValueError(f"Детермінант {det_mod} не має оберненого за модулем {mod}")

    if show_log:
        print(f"  Step 3/3: Computing {n} cofactors (circulant optimization: only 1 column)...")

    # Обчислюємо тільки перший стовпець кофакторів
    first_col_cofactors = circulant_cofactor_column(matrix_list, 0, show_progress=show_log)

    # Застосовуємо mod до кофакторів відразу для уникнення переповнення

    first_col_cofactors = [c % mod for c in first_col_cofactors]

    # Логуємо оптимізацію

    _circulant_matrix_log.append({

        'size': n,

        'determinant': det,

        'optimization': 'single_column_cofactors'

    })

    if show_log:
        print(f"  Circulant matrix inversion complete!")

    # Будуємо обернену матрицю: транспонуємо та множимо на обернений детермінант

    # Для циркулянтної матриці: cofactor[i][j] = first_col[(i - j) % n]

    # adjugate[i][j] = cofactor[j][i] = first_col[(j - i) % n]

    inv_matrix = np.zeros((n, n), dtype=np.int64)

    for i in range(n):

        for j in range(n):
            cofactor_val = first_col_cofactors[(j - i) % n]

            inv_matrix[i, j] = (inv_det * cofactor_val) % mod

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


def gcd(a, b):
    """
    Обчислює найбільший спільний дільник (НСД) двох чисел.

    Args:
        a: перше число
        b: друге число

    Returns:
        int: НСД чисел a і b
    """
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def is_coprime(a, b):
    """
    Перевіряє, чи є два числа взаємно простими (coprime).
    Числа є взаємно простими, якщо їх НСД дорівнює 1.

    Args:
        a: перше число
        b: друге число

    Returns:
        bool: True якщо числа взаємно прості, False інакше
    """
    return gcd(a, b) == 1


def validate_matrix_determinant_reversibility(matrix, modulus):
    """
    Перевіряє, чи визначник матриці оборотний за модулем (coprime).
    Для шифрування Хілла детермінант ключової матриці повинен бути взаємно простим з модулем.

    Args:
        matrix: ключова матриця
        modulus: модуль (зазвичай розмір алфавіту)

    Returns:
        tuple: (is_valid, det, error_message)
            - is_valid: True якщо детермінант оборотний
            - det: значення детермінанта
            - error_message: повідомлення про помилку (якщо is_valid = False)

    Raises:
        ValueError: якщо детермінант не оборотний за модулем
    """
    det = determinant_int(matrix)
    det_mod = det % modulus

    if det_mod == 0:
        return False, det, f"Детермінант матриці ({det}) дорівнює 0 за модулем {modulus}. Матриця не оборотна!"

    if not is_coprime(det_mod, modulus):
        gcd_value = gcd(det_mod, modulus)
        return False, det, (
            f"Детермінант матриці ({det}, mod {modulus} = {det_mod}) не є взаємно простим з модулем {modulus}.\n"
            f"НСД({det_mod}, {modulus}) = {gcd_value} ≠ 1.\n"
            f"Матриця не має оберненої за модулем {modulus} та не може бути використана для шифрування!"
        )

    return True, det, ""


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


def determinant_int(matrix, show_progress=False):
    """
    Обчислення визначника матриці з використанням ТІЛЬКИ цілих чисел.
    Використовує алгоритм Барейса (fraction-free Gaussian elimination) - O(n³).

    Args:
        matrix: квадратна матриця (numpy array або list of lists)
        show_progress: якщо True, виводить прогрес у консоль для великих матриць

    Returns:
        int: визначник матриці
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

    # Bareiss algorithm (fraction-free Gaussian elimination) - O(n³)
    # Create a working copy with Python integers for exact arithmetic
    M = [[int(matrix[i][j]) for j in range(n)] for i in range(n)]

    sign = 1  # Track sign changes from row swaps
    prev_pivot = 1  # Previous pivot for division

    for k in range(n - 1):
        # Progress logging for large matrices
        if show_progress and n >= 8:
            print(f"  Determinant calculation: step {k + 1}/{n - 1}")

        # Find pivot (non-zero element in column k)
        pivot_row = None
        for i in range(k, n):
            if M[i][k] != 0:
                pivot_row = i
                break

        if pivot_row is None:
            # Column is all zeros - determinant is 0
            return 0

        # Swap rows if needed
        if pivot_row != k:
            M[k], M[pivot_row] = M[pivot_row], M[k]
            sign = -sign

        # Bareiss elimination
        pivot = M[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                # Bareiss formula: M[i][j] = (M[k][k] * M[i][j] - M[i][k] * M[k][j]) / prev_pivot
                # This is guaranteed to divide exactly
                M[i][j] = (pivot * M[i][j] - M[i][k] * M[k][j]) // prev_pivot
            M[i][k] = 0  # Clear column below pivot

        prev_pivot = pivot

    # The determinant is the last diagonal element, adjusted for sign
    return sign * M[n - 1][n - 1]


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


def matrix_mod_inverse(matrix, mod, show_progress=True):
    """
    Обчислення оберненої матриці по модулю з цілочисельною арифметикою.
    Автоматично визначає циркулянтні матриці та використовує оптимізований алгоритм.

    Args:
        matrix: квадратна матриця
        mod: модуль
        show_progress: якщо True, виводить прогрес у консоль для великих матриць

    Returns:
        numpy array: обернена матриця за модулем
    """
    global _circulant_matrix_log

    n = matrix.shape[0]
    show_log = show_progress and n >= 8  # Show progress for matrices 8x8 and larger

    # Перевіряємо чи матриця циркулянтна
    if is_circulant_matrix(matrix):
        if show_log:
            print(f"[Optimization] Detected circulant {n}x{n} matrix - using fast algorithm")
        # Логуємо використання оптимізації (без виведення на екран)
        _circulant_matrix_log.append({
            'size': n,
            'type': 'circulant_detected',
            'optimization': 'using_circulant_inverse'
        })
        return circulant_inverse(matrix, mod, show_progress=show_progress)

    if show_log:
        print(f"[Matrix Inversion] Computing {n}x{n} matrix inverse...")
        print(f"  Step 1/3: Computing determinant...")

    det = determinant_int(matrix, show_progress=show_log)
    det_mod = det % mod

    if det_mod == 0:
        raise ValueError(f"Детермінант {det} не має оберненого за модулем {mod}")

    if show_log:
        print(f"  Step 2/3: Determinant = {det} (mod {mod} = {det_mod})")

    # Знаходимо обернений елемент детермінанта
    inv_det = None
    for x in range(1, mod):
        if (det_mod * x) % mod == 1:
            inv_det = x
            break

    if inv_det is None:
        raise ValueError(f"Детермінант {det_mod} не має оберненого за модулем {mod}")

    if show_log:
        print(f"  Step 3/3: Computing {n}x{n} cofactor matrix ({n*n} minors)...")

    # Обчислюємо матрицю кофакторів (використовуємо Python list для великих чисел)

    cofactors = [[0] * n for _ in range(n)]

    total_minors = n * n

    for i in range(n):

        for j in range(n):
            minor_det = matrix_minor(matrix, i, j)

            sign = 1 if (i + j) % 2 == 0 else -1

            # Застосовуємо mod відразу для уникнення переповнення

            cofactors[i][j] = (sign * minor_det) % mod

        # Progress update per row

        if show_log:
            done = (i + 1) * n

            print(f"    Cofactors: {done}/{total_minors} ({100 * done // total_minors}%)")

    if show_log:
        print(f"  Matrix inversion complete!")

    # Транспонуємо (adjugate = cofactors^T) та множимо на обернений детермінант

    inv_matrix = np.zeros((n, n), dtype=np.int64)

    for i in range(n):

        for j in range(n):
            # Транспонування: inv_matrix[i][j] = cofactors[j][i]

            inv_matrix[i, j] = (inv_det * cofactors[j][i]) % mod

    return inv_matrix