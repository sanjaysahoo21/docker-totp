# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import time, base64, re

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from app.totp_utils import generate_totp, verify_totp

app = FastAPI()

# candidate seed paths (container /data preferred)
SEED_CANDIDATES = [
    Path("/data/seed.txt"),        # container path
    Path("data/seed.txt"),         # repo-local path
    Path("C:/data/seed.txt"),      # Windows root fallback
]

PRIVATE_KEY_PATH = Path("student_private.pem")
HEX_RE = re.compile(r"^[0-9a-f]{64}$")

class EncryptedSeed(BaseModel):
    encrypted_seed: str

class CodeIn(BaseModel):
    code: str

def find_seed_path() -> Path | None:
    for p in SEED_CANDIDATES:
        if p.exists():
            return p
    return None

def load_private_key(path=PRIVATE_KEY_PATH):
    if not path.exists():
        raise FileNotFoundError(f"Private key missing: {path}")
    raw = path.read_bytes()
    return serialization.load_pem_private_key(raw, password=None)

@app.post("/decrypt-seed")
async def post_decrypt_seed(payload: EncryptedSeed):
    try:
        priv = load_private_key()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Private key load failed: {e}")
    # decode base64
    try:
        ct = base64.b64decode(payload.encrypted_seed)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Base64 decode failed: {e}")
    # decrypt OAEP-SHA256
    try:
        plain = priv.decrypt(
            ct,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        hex_seed = plain.decode().strip().lower()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RSA decryption failed: {e}")
    if not HEX_RE.fullmatch(hex_seed):
        raise HTTPException(status_code=500, detail="Decrypted seed invalid format")
    # write to first writable candidate (prefer /data)
    target = SEED_CANDIDATES[0]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(hex_seed)
    return {"status": "ok"}

@app.get("/generate-2fa")
async def get_generate_2fa():
    sp = find_seed_path()
    if not sp:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    hex_seed = sp.read_text().strip()
    code = generate_totp(hex_seed)
    valid_for = 30 - (int(time.time()) % 30)
    return {"code": code, "valid_for": valid_for}

@app.post("/verify-2fa")
async def post_verify_2fa(payload: CodeIn):
    if not payload.code:
        raise HTTPException(status_code=400, detail="Missing code")
    sp = find_seed_path()
    if not sp:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    hex_seed = sp.read_text().strip()
    valid = verify_totp(hex_seed, payload.code)
    return {"valid": bool(valid)}
