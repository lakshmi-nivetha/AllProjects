import hashlib
import random
from sympy import mod_inverse, isprime, randprime

# === Utility Functions ===

def sha256_hash(data: bytes) -> int:
    return int(hashlib.sha256(data).hexdigest(), 16)

def generate_large_prime(bits=512):
    return randprime(2**(bits - 1), 2**bits)

# === RSA Implementation ===

def rsa_keygen(bits=512):
    p = generate_large_prime(bits)
    q = generate_large_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    d = mod_inverse(e, phi)
    return (e, n), (d, n)

def rsa_sign(private_key, message_hash):
    d, n = private_key
    return pow(message_hash, d, n)

def rsa_verify(public_key, message_hash, signature):
    e, n = public_key
    return pow(signature, e, n) == message_hash

# === ElGamal Implementation ===

def elgamal_keygen(bits=512):
    p = generate_large_prime(bits)
    g = random.randint(2, p - 2)
    x = random.randint(1, p - 2)
    y = pow(g, x, p)
    return (p, g, y), x

def elgamal_sign(private_key, p, g, message_hash):
    x = private_key
    while True:
        k = random.randint(1, p - 2)
        if gcd(k, p - 1) == 1:
            break
    r = pow(g, k, p)
    k_inv = mod_inverse(k, p - 1)
    s = (k_inv * (message_hash - x * r)) % (p - 1)
    return (r, s)

def elgamal_verify(public_key, message_hash, signature):
    p, g, y = public_key
    r, s = signature
    if not (0 < r < p):
        return False
    v1 = (pow(y, r, p) * pow(r, s, p)) % p
    v2 = pow(g, message_hash, p)
    return v1 == v2

# === DSS (DSA) Implementation ===

def dss_keygen(bits=512):
    q = generate_large_prime(160)
    while True:
        p = q * random.randint(2**(bits - 160 - 1), 2**(bits - 160)) + 1
        if isprime(p):
            break
    h = 2
    g = pow(h, (p - 1) // q, p)
    x = random.randint(1, q - 1)
    y = pow(g, x, p)
    return (p, q, g, y), x

def dss_sign(private_key, p, q, g, message_hash):
    x = private_key
    while True:
        k = random.randint(1, q - 1)
        if gcd(k, q) == 1:
            break
    r = pow(g, k, p) % q
    k_inv = mod_inverse(k, q)
    s = (k_inv * (message_hash + x * r)) % q
    return (r, s)

def dss_verify(public_key, message_hash, signature):
    p, q, g, y = public_key
    r, s = signature
    if not (0 < r < q and 0 < s < q):
        return False
    w = mod_inverse(s, q)
    u1 = (message_hash * w) % q
    u2 = (r * w) % q
    v = ((pow(g, u1, p) * pow(y, u2, p)) % p) % q
    return v == r

# === GCD helper ===
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# === MAIN EXECUTION ===
def main():
    # Read sample file
    filename = 'sample.txt'
    try:
        with open(filename, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        data = b'This is a sample file for signature testing.'
        with open(filename, 'wb') as f:
            f.write(data)

    h = sha256_hash(data)

    # RSA
    print("\n--- RSA Digital Signature ---")
    pub_rsa, priv_rsa = rsa_keygen()
    sig_rsa = rsa_sign(priv_rsa, h)
    print("Signature:", sig_rsa)
    print("Verification:", "Success" if rsa_verify(pub_rsa, h, sig_rsa) else "Failed")

    # ElGamal
    print("\n--- ElGamal Digital Signature ---")
    pub_elg, priv_elg = elgamal_keygen()
    sig_elg = elgamal_sign(priv_elg, *pub_elg[:2], h)
    print("Signature:", sig_elg)
    print("Verification:", "Success" if elgamal_verify(pub_elg, h, sig_elg) else "Failed")

    # DSS / DSA
    print("\n--- DSS (DSA) Digital Signature ---")
    pub_dss, priv_dss = dss_keygen()
    sig_dss = dss_sign(priv_dss, *pub_dss[:3], h)
    print("Signature:", sig_dss)
    print("Verification:", "Success" if dss_verify(pub_dss, h, sig_dss) else "Failed")

if __name__ == "__main__":
    main()
