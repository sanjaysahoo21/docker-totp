from app.totp_utils import generate_totp, verify_totp

hex_seed = open("C:/data/seed.txt").read().strip()

code = generate_totp(hex_seed)
print("Current TOTP =", code)

print("Verify =", verify_totp(hex_seed, code))
