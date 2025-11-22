"""
Шаблони алфавітів
"""

ALPHABET_UKR = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"

# Base64 алфавіт для шифрування файлів
# Включає: A-Za-z0-9+/= (стандартний Base64) + . (padding) + : (для маркера EXT)
ALPHABET_BASE64 = "./:=+0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

ALPHABET_TEMPLATES = {
    "Український": ALPHABET_UKR,
    "Зворотний український": ALPHABET_UKR[::-1],
    "Англійський": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "Зворотний англійський": "ZYXWVUTSRQPONMLKJIHGFEDCBA",
    "Base64 (для файлів)": ALPHABET_BASE64
}