import base64
import subprocess
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import rsa

# Paths
PRIVATE_KEY_PATH = Path("student_private.pem")
INSTRUCTOR_PUB_PATH = Path("instructor_public.pem")

def get_commit_hash() -> str:
    out = subprocess.check_output(["git", "log", "-1", "--format=%H"])
    return out.decode().strip()

def load_private_key(p: Path):
    data = p.read_bytes()
    return serialization.load_pem_private_key(data, password=None)

def load_public_key(p: Path):
    data = p.read_bytes()
    return serialization.load_pem_public_key(data)

def sign_message(message: str, private_key) -> bytes:
    """
    Sign an ASCII message using RSA-PSS with SHA-256.
    """
    msg_bytes = message.encode("utf-8")
    signature = private_key.sign(
        msg_bytes,
        asym_padding.PSS(
            mgf=asym_padding.MGF1(hashes.SHA256()),
            salt_length=asym_padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt bytes using RSA OAEP with SHA-256.
    """
    ciphertext = public_key.encrypt(
        data,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def main():
    commit_hash = get_commit_hash()
    print("Commit Hash:", commit_hash)

    # load keys
    priv = load_private_key(PRIVATE_KEY_PATH)
    instr_pub = load_public_key(INSTRUCTOR_PUB_PATH)

    # sign
    sig = sign_message(commit_hash, priv)

    # encrypt signature with instructor public key
    ct = encrypt_with_public_key(sig, instr_pub)

    # base64 encode ciphertext (single line)
    b64 = base64.b64encode(ct).decode("ascii")
    print("Encrypted Signature (base64):", b64)

if __name__ == "__main__":
    main()
