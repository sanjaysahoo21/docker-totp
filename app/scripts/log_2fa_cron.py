#!/usr/bin/env python3
# scripts/log_2fa_cron.py
from pathlib import Path
from datetime import datetime, timezone
from app.totp_utils import generate_totp

SEED_PATHS = [Path("/data/seed.txt"), Path("data/seed.txt"), Path("C:/data/seed.txt")]

def read_seed():
    for p in SEED_PATHS:
        if p.exists():
            return p.read_text().strip()
    return None

def main():
    seed = read_seed()
    if not seed:
        print("No seed found")
        return
    code = generate_totp(seed)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} - 2FA Code: {code}")

if __name__ == "__main__":
    main()
