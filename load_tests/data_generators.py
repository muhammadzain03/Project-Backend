import random
import string
import time
from io import BytesIO

from PIL import Image


def _random_alphanumeric(length: int) -> str:
    """Generate a random alphanumeric string of the requested length."""
    if length < 1:
        raise ValueError("length must be greater than 0")

    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=length))


def generate_username(length: int = 12) -> str:
    """Generate an alphanumeric username."""
    return _random_alphanumeric(length)


def generate_password(length: int = 16) -> str:
    """Generate an alphanumeric password."""
    return _random_alphanumeric(length)


def generate_email(domain: str = "example.com") -> str:
    """Generate a likely-unique email using a timestamp and random suffix."""
    timestamp = int(time.time() * 1000)
    local_part = f"u{timestamp}{_random_alphanumeric(6)}"
    return f"{local_part}@{domain}"


def random_png_bytes(width: int = 512, height: int = 512) -> bytes:
    """Generate random colored PNG bytes with the requested dimensions."""
    image = Image.new("RGB", (width, height))
    pixels = [
        (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        for _ in range(width * height)
    ]
    image.putdata(pixels)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def random_png_file(path: str, width: int = 512, height: int = 512) -> str:
    """Create a random colored PNG file and return its path."""
    data = random_png_bytes(width=width, height=height)
    with open(path, "wb") as file_obj:
        file_obj.write(data)
    return path
