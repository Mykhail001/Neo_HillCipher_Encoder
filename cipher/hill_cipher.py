"""
Реалізація шифру Хілла
"""

import numpy as np
import secrets
from utils.math_utils import matrix_mod_inverse


def get_case_conversion_mode(alphabet):
    """
    Визначає режим конвертації регістру на основі складу алфавіту.

    Повертає:
    - 'upper': якщо алфавіт містить великі літери і не містить малих
    - 'lower': якщо алфавіт містить малі літери і не містить великих
    - None: якщо алфавіт містить обидва регістри або не містить літер
    """
    has_upper = False
    has_lower = False

    for char in alphabet:
        if char.isupper() and char.lower() in alphabet:
            # Є пара великої і малої літери - не конвертуємо
            return None
        if char.isupper():
            has_upper = True
        if char.islower():
            has_lower = True

    # Якщо є тільки великі літери - конвертуємо в великі
    if has_upper and not has_lower:
        return 'upper'

    # Якщо є тільки малі літери - конвертуємо в малі
    if has_lower and not has_upper:
        return 'lower'

    # Інакше не конвертуємо
    return None


def text_to_numbers(text, alphabet):
    """Конвертує текст в числа згідно з алфавітом"""
    if not isinstance(text, str):
        raise ValueError("Очікується текст, але отримано інший тип.")

    # Визначаємо режим конвертації регістру
    case_mode = get_case_conversion_mode(alphabet)

    result = []
    for char in text:
        # Застосовуємо конвертацію регістру якщо потрібно
        converted_char = char
        if case_mode == 'upper':
            converted_char = char.upper()
        elif case_mode == 'lower':
            converted_char = char.lower()

        # Додаємо тільки ті символи, які є в алфавіті
        if converted_char in alphabet:
            result.append(alphabet.index(converted_char))

    return result


def numbers_to_text(numbers, alphabet):
    """Конвертує числа в текст згідно з алфавітом"""
    return ''.join(alphabet[num] for num in numbers if 0 <= num < len(alphabet))


def hill_encrypt_standard(numbers, key_matrix, alph):
    """Стандартне шифрування Хілла"""
    n = len(key_matrix)
    mod_val = len(alph)

    numbers = numbers.copy()
    while len(numbers) % n != 0:
        numbers.append(0)

    encrypted_numbers = []
    mat = np.array(key_matrix, dtype=np.int64)

    for i in range(0, len(numbers), n):
        block = numbers[i:i + n]
        vec = np.array(block, dtype=np.int64)
        res = np.dot(mat, vec)
        res = np.mod(res, mod_val).astype(int)
        encrypted_numbers.extend(res.tolist())

    return encrypted_numbers


def hill_encrypt_modified(text, key_matrix, alph, subst_map, noise_length=0):
    """
    Модифіковане шифрування Хілла з підстановкою і шумом

    Алгоритм:
    1. Розбити текст на блоки (matrix_size - noise_length) корисних символів
    2. Додати noise_length випадкових символів до кожного блоку
    3. Останній блок: {залишок тексту}{padding}{шум}
    4. Множення на матрицю
    5. Застосування підстановки (block_index + 1) разів
    """
    numbers = text_to_numbers(text, alph)
    n = len(key_matrix)
    mod_val = len(alph)
    mat = np.array(key_matrix, dtype=np.int64)

    if noise_length < 0:
        raise ValueError("Довжина шуму має бути >= 0")

    if noise_length >= n:
        raise ValueError(f"Довжина шуму ({noise_length}) має бути менше розміру матриці ({n})")

    # Розмір корисної частини блоку
    useful_size = n - noise_length

    encrypted_numbers = []
    block_index = 0

    # Обробка блоків
    i = 0
    while i < len(numbers):
        # Беремо корисні символи
        useful_part = numbers[i:i + useful_size]

        # Формуємо блок
        if len(useful_part) == useful_size:
            # Повний блок: корисні символи + шум
            noise = [secrets.randbelow(mod_val) for _ in range(noise_length)]
            block = useful_part + noise
        else:
            # Останній неповний блок: корисні символи + padding + шум
            padding_needed = useful_size - len(useful_part)
            padding = [0] * padding_needed  # Padding символом з індексом 0
            noise = [secrets.randbelow(mod_val) for _ in range(noise_length)]
            block = useful_part + padding + noise

        # Множення на матрицю
        vec = np.array(block, dtype=np.int64)
        res = np.dot(mat, vec)
        res = np.mod(res, mod_val).astype(int).tolist()

        # Застосування підстановки (block_index + 1) разів
        times_to_substitute = block_index + 1
        for _ in range(times_to_substitute):
            res = [subst_map[x % len(subst_map)] for x in res]

        encrypted_numbers.extend(res)

        i += useful_size
        block_index += 1

    return "".join(alph[num % mod_val] for num in encrypted_numbers)


def hill_decrypt_standard(ciphertext_numbers, key_matrix, alph):
    """Стандартне розшифрування Хілла"""
    n = len(key_matrix)
    mod_val = len(alph)

    key_matrix_np = np.array(key_matrix, dtype=np.int64)
    inv_key = matrix_mod_inverse(key_matrix_np, mod_val)

    if len(ciphertext_numbers) % n != 0:
        raise ValueError("Довжина зашифрованого тексту некоректна.")

    decrypted_numbers = []
    for i in range(0, len(ciphertext_numbers), n):
        block = ciphertext_numbers[i:i + n]
        vec = np.array(block, dtype=np.int64)
        res = np.dot(inv_key, vec)
        res = np.mod(res, mod_val).astype(int)
        decrypted_numbers.extend(res.tolist())

    return decrypted_numbers


def hill_decrypt_modified(text, key_matrix, alph, subst_map, noise_length=0):
    """
    Модифіковане розшифрування Хілла з підстановкою і шумом

    Алгоритм:
    1. Розбити на блоки matrix_size
    2. Застосувати зворотну підстановку (block_index + 1) разів
    3. Множення на обернену матрицю
    4. Видалити noise_length символів з кінця кожного блоку
    """
    n = len(key_matrix)
    mod_val = len(alph)
    key_matrix_np = np.array(key_matrix, dtype=np.int64)
    inv_key = matrix_mod_inverse(key_matrix_np, mod_val)

    ciphertext_numbers = text_to_numbers(text, alph)

    if len(ciphertext_numbers) % n != 0:
        raise ValueError("Довжина зашифрованого тексту некоректна.")

    if noise_length < 0:
        raise ValueError("Довжина шуму має бути >= 0")

    if noise_length >= n:
        raise ValueError(f"Довжина шуму ({noise_length}) має бути менше розміру матриці ({n})")

    # Якщо немає підстановки - стандартне розшифрування
    if not subst_map:
        decrypted_numbers = []
        for i in range(0, len(ciphertext_numbers), n):
            block = ciphertext_numbers[i:i + n]
            vec = np.array(block, dtype=np.int64)
            res = np.dot(inv_key, vec)
            res = np.mod(res, mod_val).astype(int)
            decrypted_numbers.extend(res.tolist())
        return numbers_to_text(decrypted_numbers, alph)

    # Створення оберненої підстановки
    n_subst = len(subst_map)
    inv_subst = [0] * n_subst
    for i, val in enumerate(subst_map):
        inv_subst[val % n_subst] = i

    # Розмір корисної частини блоку
    useful_size = n - noise_length

    # Реверсування підстановки і розшифрування
    decrypted_useful_parts = []

    for block_index, i in enumerate(range(0, len(ciphertext_numbers), n)):
        block = ciphertext_numbers[i:i + n]
        block_times = block_index + 1

        # Застосування зворотної підстановки
        for _ in range(block_times):
            block = [inv_subst[x % n_subst] for x in block]

        # Розшифрування блоку
        vec = np.array(block, dtype=np.int64)
        res = np.dot(inv_key, vec)
        res = np.mod(res, mod_val).astype(int).tolist()

        # Видалення шуму (останні noise_length елементів)
        useful_part = res[:useful_size]
        decrypted_useful_parts.extend(useful_part)

    return numbers_to_text(decrypted_useful_parts, alph)