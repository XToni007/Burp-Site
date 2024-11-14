# utils/__init__.py (bisa kosong)

# utils/utils.py
import os

def save_to_file(directory, filename, content):
    """Save content to a file in the specified directory."""
    filepath = os.path.join(directory, f"{filename}.txt")
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)

def read_file(directory, filename):
    """Read the content of a file from the given directory."""
    filepath = os.path.join(directory, f"{filename}.txt")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    return None
