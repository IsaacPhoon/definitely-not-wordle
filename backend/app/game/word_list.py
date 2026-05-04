import random
from pathlib import Path

_target_words: list[str] = []
_valid_words: set[str] = set()

_WORDS_DIR = Path(__file__).resolve().parent.parent.parent


def load_words() -> None:
    global _target_words, _valid_words
    _target_words = (
        (_WORDS_DIR / "words_target.txt").read_text().strip().splitlines()
    )
    valid_list = (
        (_WORDS_DIR / "words_valid.txt").read_text().strip().splitlines()
    )
    _valid_words = set(valid_list) | set(_target_words)


def get_random_target() -> str:
    return random.choice(_target_words)


def is_valid_guess(word: str) -> bool:
    return word.lower() in _valid_words
