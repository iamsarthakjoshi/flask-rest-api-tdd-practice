import secrets
import hashlib
import hmac
import math
import time


def generate_shared_secret() -> str:
    return secrets.token_hex(16)


def dynamic_truncation(raw_key: hmac.HMAC, length: int) -> str:
    bitstring = bin(int(raw_key.hexdigest(), base=16))
    last_four_bits = bitstring[-4:]
    offset = int(last_four_bits, base=2)
    chosen_32_bits = bitstring[offset * 8 : offset * 8 + 32]
    full_totp = str(int(chosen_32_bits, base=2))

    return full_totp[-length:]


def generate_totp(shared_key: str, length: int = 6) -> str:
    now_in_seconds = math.floor(time.time())
    print("now_in_seconds", now_in_seconds)
    step_in_seconds = 1000  # play with this value for token expiry time
    t = math.floor(now_in_seconds / step_in_seconds)
    hash = hmac.new(
        bytes(shared_key, encoding="utf-8"),
        t.to_bytes(length=8, byteorder="big"),
        hashlib.sha256,
    )

    return dynamic_truncation(hash, length)


def validate_totp(totp: str, shared_key: str) -> bool:
    return totp == generate_totp(shared_key)


# secret = generate_shared_secret()
# print(f"Done. It is: {secret}")

# totp = generate_totp(secret)
# print(f"Done. It is: {totp}")

# secret = "65fe36fab8fad1262af2f9b3c529a8c7"
# totp="427621"

# print("Validating One-Time Password...")
# if validate_totp(totp, secret):
#   print("It is valid!")
# else:
#   print("It is invalid.")
