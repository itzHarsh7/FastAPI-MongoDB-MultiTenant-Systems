import random
import string
from database import db

async def generate_random_password(length: int = 12) -> str:

    # Character sets
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*()-_=+[]{}|;:,.<>?/"

    # Ensure at least one character from each set
    password = [
        random.choice(lower),
        random.choice(upper),
        random.choice(digits),
        random.choice(special)
    ]

    # Fill the rest with random characters from all sets combined
    all_chars = lower + upper + digits + special
    password += random.choices(all_chars, k=length)

    # Shuffle to avoid predictable patterns
    random.shuffle(password)

    return ''.join(password)


async def generate_unique_username(first_name: str, last_name: str) -> str:

    base_username = f"{first_name.lower()}.{last_name.lower()}"

    while True:
        # Random suffix
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits))
        username = f"{base_username}{suffix}"

        # Check if username exists in db
        existing_user = await db.users.find_one({"username": username})
        if not existing_user:
            return username
