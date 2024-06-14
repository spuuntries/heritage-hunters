from typing import Optional
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes


def derive_key(
    plaintext, salt: Optional[bytes] = None, iterations=100000, key_length=32
):
    if salt is None:
        salt = get_random_bytes(128)  # Generate a random salt if not provided

    password = plaintext.encode("utf-8")  # Convert plaintext to bytes

    # Derive the key using PBKDF2
    key = PBKDF2(
        password, salt, dkLen=key_length, count=iterations, hmac_hash_module=SHA256
    )

    return key.hex() + "|" + salt.hex()
