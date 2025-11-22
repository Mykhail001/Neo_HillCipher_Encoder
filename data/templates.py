"""
Шаблони алфавітів
"""

ALPHABET_UKR = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"

ALPHABET_TEMPLATES = {
    "Український": ALPHABET_UKR,
    "Зворотний український": ALPHABET_UKR[::-1],
    "Англійський": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "Зворотний англійський": "ZYXWVUTSRQPONMLKJIHGFEDCBA",
    "Base64-доповнений": "+./0123456789:=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
}