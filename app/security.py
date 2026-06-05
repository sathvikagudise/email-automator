import os
from cryptography.fernet import Fernet

KEY_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
KEY_FILE = os.path.join(KEY_DIR, "secret.key")


def generate_key():
    os.makedirs(KEY_DIR, exist_ok=True)
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key


def load_key():
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()


cipher = Fernet(load_key())


def encrypt_message(message: str) -> str:
    return cipher.encrypt(message.encode()).decode()


def decrypt_message(encrypted_message: str) -> str:
    return cipher.decrypt(encrypted_message.encode()).decode()


if __name__ == "__main__":
    msg = "This is a secret email!"
    enc_msg = encrypt_message(msg)
    dec_msg = decrypt_message(enc_msg)

    print(f"Encrypted: {enc_msg}")
    print(f"Decrypted: {dec_msg}")
