import sys
import base64
import re
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

SEED_OUTPUT_PATH = Path("/data/seed.txt")  # container path; locally it will create /data in CWD
DEFAULT_PRIVATE_KEY = Path("student_private.pem")

HEX_SEED_RE = re.compile(r"^[0-9a-f]{64}$")

def load_private_key(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Private key not found: {path}")
    raw = path.read_bytes()
    try:
        priv = serialization.load_pem_private_key(raw, password=None)
    except Exception as e:
        raise ValueError(f"Failed to parse private key: {e}")
    return priv

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    # 1. base64 decode
    try:
        ct = base64.b64decode(encrypted_seed_b64)
    except Exception as e:
        raise ValueError(f"Base64 decode failed: {e}")
    # 2. RSA/OAEP-SHA256 decrypt
    try:
        plain = private_key.decrypt(
            ct,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        raise ValueError(f"RSA decryption failed: {e}")
    # 3. decode and validate
    try:
        s = plain.decode("utf-8").strip().lower()
    except Exception as e:
        raise ValueError(f"UTF-8 decode failed: {e}")
    if not HEX_SEED_RE.fullmatch(s):
        raise ValueError(f"Decrypted seed is invalid format (expected 64 hex chars). Got: {s!r}")
    return s

def main(argv):
    if len(argv) >= 2:
        inp_path = Path(argv[1])
    else:
        inp_path = Path("encrypted_seed.txt")

    if not inp_path.exists():
        print(f"ERROR: encrypted seed file not found: {inp_path}")
        sys.exit(2)

    encrypted_seed = inp_path.read_text().strip()
    if not encrypted_seed:
        print("ERROR: encrypted_seed.txt is empty")
        sys.exit(2)

    # load private key
    try:
        private_key = load_private_key(DEFAULT_PRIVATE_KEY)
    except Exception as e:
        print("ERROR loading private key:", e)
        sys.exit(3)

    # decrypt
    try:
        hex_seed = decrypt_seed(encrypted_seed, private_key)
    except Exception as e:
        print("ERROR decrypting seed:", e)
        sys.exit(4)

    # ensure /data exists (if running locally it will create ./data)
    out_dir = SEED_OUTPUT_PATH.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    # save
    SEED_OUTPUT_PATH.write_text(hex_seed)
    print("OK: Seed decrypted and saved to", SEED_OUTPUT_PATH)
    print("Seed (first 8 chars):", hex_seed[:8] + "… (hidden)")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
