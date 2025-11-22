"""
Шаблони алфавітів
"""

ALPHABET_UKR = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"

# Base64 алфавіт для шифрування файлів
# Включає: A-Za-z0-9+/= (стандартний Base64) + . (padding) + : (для маркера EXT)
ALPHABET_BASE64 = "./:=+0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

# Англійський алфавіт з великими та малими літерами
ALPHABET_ENG_MIXED = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

# Український алфавіт з великими та малими літерами
ALPHABET_UKR_LOWER = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
ALPHABET_UKR_MIXED = ALPHABET_UKR + ALPHABET_UKR_LOWER

ALPHABET_TEMPLATES = {
    "Український": ALPHABET_UKR,
    "Зворотний український": ALPHABET_UKR[::-1],
    "Український (великі + малі)": ALPHABET_UKR_MIXED,
    "Англійський": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "Зворотний англійський": "ZYXWVUTSRQPONMLKJIHGFEDCBA",
    "Англійський (великі + малі)": ALPHABET_ENG_MIXED,
    "Base64 (для файлів)": ALPHABET_BASE64
}