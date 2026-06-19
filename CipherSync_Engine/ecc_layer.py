from reedsolo import RSCodec, ReedSolomonError

class ErrorCorrectionEngine:
    def __init__(self, ecc_symbols=32):
        """
        Initializes the Reed-Solomon Codec.
        :param ecc_symbols: The number of parity bytes added per chunk. 
                            32 symbols means we can heal up to 16 corrupted bytes per chunk.
        """
        self.ecc_symbols = ecc_symbols
        # The maximum block size in GF(2^8) is 255. 
        # So, Data Chunk + Parity Symbols must equal 255.
        self.chunk_size = 255 - self.ecc_symbols 
        self.rsc = RSCodec(self.ecc_symbols)

    def encode_payload(self, encrypted_bytes: bytes) -> bytes:
        """Slices the payload, adds parity symbols to each slice, and reassembles."""
        encoded_full = bytearray()
        
        # Process the file in specific chunk sizes
        for i in range(0, len(encrypted_bytes), self.chunk_size):
            chunk = encrypted_bytes[i:i + self.chunk_size]
            # rsc.encode() automatically appends the parity bytes to the end of the chunk
            encoded_full.extend(self.rsc.encode(chunk))
            
        return bytes(encoded_full)

    def decode_payload(self, corrupted_bytes: bytes) -> bytes:
        """Detects errors, heals the corrupted bytes, and strips the parity symbols."""
        decoded_full = bytearray()
        block_size = 255 # Reassembling requires looking at the full 255-byte blocks
        
        try:
            for i in range(0, len(corrupted_bytes), block_size):
                chunk = corrupted_bytes[i:i + block_size]
                
                # decode() returns a tuple. Index [0] is the healed original data.
                # If there are more than 16 errors in this chunk, it raises an exception.
                healed_chunk = self.rsc.decode(chunk)[0]
                decoded_full.extend(healed_chunk)
                
            return bytes(decoded_full)
            
        except ReedSolomonError as e:
            raise ValueError(f"[-] FATAL: Image corruption exceeds recovery threshold! {e}")

# ==========================================
# VERIFICATION ROUTINE (The "Bit-Flip" Test)
# ==========================================
if __name__ == "__main__":
    print("[*] Initializing Reed-Solomon Shield...")
    ecc = ErrorCorrectionEngine(ecc_symbols=32)
    
    # 1. Create a mock encrypted payload
    original_data = b"AES_GCM_ENCRYPTED_PAYLOAD_DATA_THAT_MUST_NOT_BE_CORRUPTED" * 4
    print(f"[+] Original Data Length: {len(original_data)} bytes")
    
    # 2. Encode it with parity bytes
    armored_data = bytearray(ecc.encode_payload(original_data))
    print(f"[+] Armored Data Length: {len(armored_data)} bytes (Includes Parity Overhead)")
    
    # 3. Simulate Image Compression / Steganography Damage
    print("\n[*] Simulating forensic damage... flipping random bytes...")
    # Let's deliberately corrupt 10 random bytes
    armored_data[5] = 0xFF
    armored_data[12] = 0x00
    armored_data[40] = 0xAA
    armored_data[88] = 0x11
    # ... pretend more bytes are corrupted ...
    
    # 4. Attempt to Heal
    print("[*] Passing corrupted data to the ECC Decoder...")
    try:
        healed_data = ecc.decode_payload(bytes(armored_data))
        if healed_data == original_data:
            print("[+] SUCCESS: Reed-Solomon mathematically reconstructed the destroyed bytes!")
            print(f"[+] Recovered Data Preview: {healed_data[:50]}...")
    except ValueError as e:
        print(e)
