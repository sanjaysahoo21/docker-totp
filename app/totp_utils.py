# app/totp_utils.py
import binascii, base64, pyotp

def hex_to_base32(hex_seed: str) -> str:
    b = binascii.unhexlify(hex_seed)
    return base64.b32encode(b).decode()

def generate_totp(hex_seed: str) -> str:
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, digits=6, interval=30)
    return totp.now()

def verify_totp(hex_seed: str, code: str) -> bool:
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, digits=6, interval=30)
    return totp.verify(code, valid_window=1)
