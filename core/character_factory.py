import random
from core.characters import CHARACTERS


def get_random_characters(amount=5):
    return random.sample(CHARACTERS, amount)