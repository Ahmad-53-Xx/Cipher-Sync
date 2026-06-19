import hashlib
import random

class PathScatterEngine:
    def __init__(self, total_blocks: int):
        self.total_blocks = total_blocks

    def _generate_seed_from_key(self, crypto_key: bytes) -> int:
        """Derives a deterministic integer seed from the cryptographic key using SHA-256."""
        hashed = hashlib.sha256(crypto_key).digest()
        # Convert the first 8 bytes of the hash into a large integer to seed the PRNG
        return int.from_bytes(hashed[:8], byteorder='big')

    def generate_block_path(self, crypto_key: bytes) -> list:
        """
        Creates a pseudo-random, non-repeating sequence of block indices.
        The path is completely reproducible given the same cryptographic key.
        """
        # 1. Initialize a linear list of all available block indices
        linear_path = list(range(self.total_blocks))
        
        # 2. Derive the deterministic seed
        seed = self._generate_seed_from_key(crypto_key)
        
        # 3. Use an isolated random instance to prevent interfering with global state
        local_prng = random.Random(seed)
        
        # 4. Shuffle the indices using the Fisher-Yates algorithm implementation inside random
        local_prng.shuffle(linear_path)
        
        return linear_path

# ==========================================
# VERIFICATION ROUTINE
# ==========================================
if __name__ == "__main__":
    print("[*] Initializing Path Scatter Engine...")
    
    # Simulate a standard image with 32,400 available 8x8 blocks
    mock_total_blocks = 32400
    scatter_system = PathScatterEngine(total_blocks=mock_total_blocks)
    
    # Simulated 256-bit AES key from Phase 1
    mock_key = b'\x01' * 32 
    
    print("[*] Generating scattered injection path...")
    path = scatter_system.generate_block_path(mock_key)
    
    print(f"[+] Total indices mapped: {len(path)}")
    print(f"[+] First 10 target block indices: {path[:10]}")
    print(f"[+] Last 10 target block indices: {path[-10:]}")
    
    # Verify uniqueness
    assert len(set(path)) == mock_total_blocks, "Error: Duplicate indices detected in path generation!"
    print("[+] Structural integrity check passed: Path contains zero duplicate locations.")
