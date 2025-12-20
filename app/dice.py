import random
from typing import Tuple


def d20() -> int:
    return random.randint(1, 20)


def d100() -> int:
    return random.randint(1, 100)


def roll_ndm(n: int, m: int) -> Tuple[int, list[int]]:
    rolls = [random.randint(1, m) for _ in range(n)]
    return sum(rolls), rolls
