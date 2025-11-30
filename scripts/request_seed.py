# scripts/request_seed.py
import requests
from pathlib import Path

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"
STUDENT_ID = "23P31A05F2"
GITHUB_REPO_URL = "https://github.com/sanjaysahoo21/docker-totp.git"
PUBKEY_PATH = Path("student_public.pem")
OUT_PATH = Path("encrypted_seed.txt")

def read_public_key_raw(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    # Basic sanity checks
    if "BEGIN PUBLIC KEY" not in raw:
        raise SystemExit("student_public.pem missing BEGIN PUBLIC KEY header")
    return raw  # return with real newline characters

def request_seed():
    pk_raw = read_public_key_raw(PUBKEY_PATH)
    payload = {
        "student_id": STUDENT_ID,
        "github_repo_url": GITHUB_REPO_URL,
        "public_key": pk_raw
    }
    headers = {"Content-Type": "application/json"}
    print("Sending request to instructor API...")
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
    try:
        resp.raise_for_status()
    except Exception as e:
        print("HTTP error:", e)
        print("Response status:", resp.status_code)
        print("Response body:", resp.text)
        raise

    j = resp.json()
    if j.get("status") != "success":
        print("API returned error:", j)
        raise SystemExit("Instructor API did not return success")
    enc = j.get("encrypted_seed")
    if not enc:
        raise SystemExit("No encrypted_seed field in response")
    OUT_PATH.write_text(enc.strip())
    print("Saved encrypted_seed.txt (DO NOT commit this file).")
    print("First 8 chars:", enc.strip()[:8] + "…")
    return enc.strip()

if __name__ == "__main__":
    request_seed()
