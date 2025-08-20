import random
import string


def generate_temporary_password(length: int = 8) -> str:
    """
    Generate a temporary password with letters and numbers.
    """
    # Use uppercase, lowercase, and digits
    characters = string.ascii_letters + string.digits

    # Ensure at least one uppercase, one lowercase, and one digit
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
    ]

    # Fill the rest of the password
    for _ in range(length - 3):
        password.append(random.choice(characters))

    # Shuffle the password
    random.shuffle(password)

    return "".join(password)
