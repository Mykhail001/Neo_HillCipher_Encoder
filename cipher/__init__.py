"""
Модулі шифрування
"""

from .hill_cipher import (
    text_to_numbers,
    numbers_to_text,
    hill_encrypt_standard,
    hill_encrypt_modified,
    hill_decrypt_standard,
    hill_decrypt_modified
)

from .substitution import (
    generate_random_substitution,
    create_shift_substitution,
    create_reverse_substitution,
    invert_substitution,
    validate_substitution,
    apply_substitution,
    apply_substitution_multiple,
    compose_substitutions,
    substitution_order,
    substitution_to_string,
    string_to_substitution,
    get_template_substitution,
    SUBSTITUTION_TEMPLATES
)

__all__ = [
    # Hill Cipher
    'text_to_numbers',
    'numbers_to_text',
    'hill_encrypt_standard',
    'hill_encrypt_modified',
    'hill_decrypt_standard',
    'hill_decrypt_modified',
    # Substitution
    'generate_random_substitution',
    'create_shift_substitution',
    'create_reverse_substitution',
    'invert_substitution',
    'validate_substitution',
    'apply_substitution',
    'apply_substitution_multiple',
    'compose_substitutions',
    'substitution_order',
    'substitution_to_string',
    'string_to_substitution',
    'get_template_substitution',
    'SUBSTITUTION_TEMPLATES'
]