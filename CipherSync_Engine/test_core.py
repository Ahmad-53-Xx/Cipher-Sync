import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

class CryptoCore:
    def __init__(self):
        self.iterations = 600_000 

    def derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32, 
            salt=salt,
            iterations=self.iterations,
        )
        return kdf.derive(password.encode())

    def encrypt_payload(self, raw_data: bytes, password: str) -> bytes:
        salt = os.urandom(16)
        nonce = os.urandom(12) 
        key = self.derive_key(password, salt)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, raw_data, associated_data=None)
        return salt + nonce + ciphertext

    def decrypt_payload(self, encrypted_payload: bytes, password: str) -> bytes:
        salt = encrypted_payload[:16]
        nonce = encrypted_payload[16:28]
        ciphertext = encrypted_payload[28:]
        key = self.derive_key(password, salt)
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, associated_data=None)

# ==========================================
# TESTING ROUTINE
# ==========================================
if __name__ == "__main__":
    print("[*] Initializing CryptoCore...")
    core = CryptoCore()
    master_password = "SuperSecretMasterPassword2026!"
    
    # 1. Create a dummy file
    test_filename = "my_secret_research.txt"
    with open(test_filename, "w") as f:
        f.write("This is highly sensitive data for my Master's Degree. Do not share.")
    print(f"[+] Created test file: {test_filename}")

    # 2. Read and Encrypt
    with open(test_filename, "rb") as f:
        raw_data = f.read()
    
    print("[*] Encrypting data (this might take a second due to high PBKDF2 iterations)...")
    encrypted_data = core.encrypt_payload(raw_data, master_password)
    
    encrypted_filename = "vault_payload.bin"
    with open(encrypted_filename, "wb") as f:
        f.write(encrypted_data)
    print(f"[+] Encryption successful! Saved as: {encrypted_filename}")
    print(f"    -> Original Size: {len(raw_data)} bytes")
    print(f"    -> Encrypted Size: {len(encrypted_data)} bytes (includes Salt + Nonce + Auth Tag)")

    # 3. Read and Decrypt (Success Case)
    print("\n[*] Attempting legitimate decryption...")
    with open(encrypted_filename, "rb") as f:
        data_to_decrypt = f.read()
    
    decrypted_data = core.decrypt_payload(data_to_decrypt, master_password)
    decrypted_filename = "decrypted_research.txt"
    with open(decrypted_filename, "wb") as f:
        f.write(decrypted_data)
    print(f"[+] Decryption successful! Recovered data saved to: {decrypted_filename}")

    # 4. Read and Decrypt (Tamper/Wrong Password Case)
    print("\n[*] Attempting decryption with the WRONG password to test AES-GCM security...")
    try:
        core.decrypt_payload(data_to_decrypt, "WrongPassword123!")
        print("[-] DANGER: Decryption succeeded when it should have failed!")
    except InvalidTag:
        print("[+] SUCCESS: AES-GCM blocked the decryption. (InvalidTag raised: Bad password or tampered data).")

    # Cleanup
    print("\n[*] Test complete. Check your directory for the generated files.")
