import random
import string


def generate(length=16):
    """
    Generate a strong Password
    """

    return "".join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )
