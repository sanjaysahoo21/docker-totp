from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_keypair(key_size: int = 4096):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    public_key = private_key.public_key()
    # private PEM
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,  # or PKCS8
        encryption_algorithm=serialization.NoEncryption()
    )
    # public PEM
    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return priv_pem, pub_pem

if __name__ == "__main__":
    priv_pem, pub_pem = generate_rsa_keypair()
    open("student_private.pem","wb").write(priv_pem)
    open("student_public.pem","wb").write(pub_pem)
    print("Wrote student_private.pem and student_public.pem")
