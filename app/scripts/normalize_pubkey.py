# scripts/normalize_pubkey.py
from pathlib import Path

src = Path("student_public.pem")
if not src.exists():
    raise SystemExit("student_public.pem not found")

raw = src.read_bytes()

# Remove UTF-8 BOM if present
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]

# Decode tolerant, then re-encode as UTF-8 without BOM and with LF
text = raw.decode('utf-8', errors='strict').replace('\r\n', '\n').replace('\r', '\n')
# Ensure trailing newline at EOF
if not text.endswith('\n'):
    text += '\n'
src.write_text(text, encoding='utf-8')
print("Normalized student_public.pem to UTF-8 (no BOM) and LF endings.")
print("First line:", text.splitlines()[0])
