import os
import sys
import time
import hashlib
import js2pysecrets as secrets
import jpegio as jio

# Ensures Python can find your module files no matter where you run the script from
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_core import CryptoCore
from ecc_layer import ErrorCorrectionEngine
from path_scatter import PathScatterEngine
from dct_injector import QuantizedDCTInjector

class CipherSyncVault:
    def __init__(self, master_password: str):
        self.master_password = master_password
        self.crypto = CryptoCore()
        self.ecc = ErrorCorrectionEngine(ecc_symbols=32)
        self.injector = QuantizedDCTInjector()

    # ==========================================
    # STANDARD PIPELINE (1-TO-1 VAULT)
    # ==========================================
    def hide_file(self, target_filepath: str, carrier_image_path: str, output_image_path: str):
        print(f"\n[>>>] STARTING FORWARD PIPELINE: {target_filepath}")
        start_time = time.time()

        if not os.path.exists(carrier_image_path):
            raise FileNotFoundError(f"[-] Carrier image missing at: {carrier_image_path}")

        with open(target_filepath, "rb") as f:
            raw_data = f.read()

        # 1. Encrypt & Armor
        encrypted_payload = self.crypto.encrypt_payload(raw_data, self.master_password)
        armored_bytes = self.ecc.encode_payload(encrypted_payload)
        
        # 2. Attach Length Header (4 bytes)
        payload_len = len(armored_bytes)
        length_header = payload_len.to_bytes(4, byteorder='big')
        final_payload = length_header + armored_bytes
        
        binary_string = ''.join([format(b, '08b') for b in final_payload])

        # 3. Dynamic Matrix Scan & Scatter
        jpeg_struct = jio.read(carrier_image_path)
        img_h, img_w = jpeg_struct.coef_arrays[0].shape
        actual_total_blocks = (img_h // 8) * (img_w // 8)
        
        scatter = PathScatterEngine(total_blocks=actual_total_blocks) 
        path_seed = hashlib.sha256(self.master_password.encode()).digest()
        prng_path = scatter.generate_block_path(path_seed)

        # 4. Inject
        self.injector.inject_payload(carrier_image_path, binary_string, prng_path, output_image_path)
        print(f"[+] FORWARD PIPELINE COMPLETE. (Elapsed: {time.time() - start_time:.2f}s)")

    def extract_file(self, stego_image_path: str, output_filepath: str):
        print(f"\n[<<<] STARTING REVERSE PIPELINE: {stego_image_path}")
        start_time = time.time()

        if not os.path.exists(stego_image_path):
            raise FileNotFoundError("[-] Stego image not found!")

        # 1. Rebuild Path
        jpeg_struct = jio.read(stego_image_path)
        img_h, img_w = jpeg_struct.coef_arrays[0].shape
        actual_total_blocks = (img_h // 8) * (img_w // 8)
        
        scatter = PathScatterEngine(total_blocks=actual_total_blocks)
        path_seed = hashlib.sha256(self.master_password.encode()).digest()
        prng_path = scatter.generate_block_path(path_seed)

        # 2. Extract max bits safely
        max_bits = actual_total_blocks 
        extracted_bits = self.injector.extract_payload(stego_image_path, prng_path, max_bits)

        # 3. Parse Header (First 32 bits = 4 bytes)
        header_bits = extracted_bits[:32]
        payload_byte_length = int.from_bytes(int(header_bits, 2).to_bytes(4, byteorder='big'), byteorder='big')
        
        # 4. Slice exact payload
        target_bit_length = payload_byte_length * 8
        payload_bits = extracted_bits[32:32 + target_bit_length]
        
        armored_bytes = bytearray()
        for i in range(0, len(payload_bits), 8):
            byte = payload_bits[i:i+8]
            if len(byte) == 8:
                armored_bytes.append(int(byte, 2))
                
        # 5. Heal & Decrypt
        print("  [*] Healing data with Reed-Solomon...")
        healed_encrypted_payload = self.ecc.decode_payload(bytes(armored_bytes))
        
        print("  [*] Verifying GCM Tag & Decrypting...")
        raw_data = self.crypto.decrypt_payload(healed_encrypted_payload, self.master_password)
        
        with open(output_filepath, "wb") as f:
            f.write(raw_data)
        
        print(f"[+] REVERSE PIPELINE COMPLETE. Recovered in {time.time() - start_time:.2f}s")


    # ==========================================
    # DISTRIBUTED PIPELINE (SHAMIR'S PHASE 3)
    # ==========================================
    def hide_file_distributed(self, target_filepath: str, carrier_images: list, output_dir: str, threshold: int):
        print(f"\n[>>>] STARTING DISTRIBUTED PIPELINE: {target_filepath}")
        start_time = time.time()

        total_shares = len(carrier_images)
        if threshold > total_shares:
            raise ValueError("[-] Threshold cannot be greater than the total number of carrier images.")

        with open(target_filepath, "rb") as f:
            raw_data = f.read()

        encrypted_payload = self.crypto.encrypt_payload(raw_data, self.master_password)
        armored_bytes = self.ecc.encode_payload(encrypted_payload)
        
        print(f"  [*] Splitting payload into {total_shares} shares (Requires {threshold} to reconstruct)...")
        payload_hex = armored_bytes.hex()
        shares_hex = secrets.share(payload_hex, total_shares, threshold)

        for index, (share_hex, carrier_path) in enumerate(zip(shares_hex, carrier_images)):
            share_bytes = bytes.fromhex(share_hex)
            
            share_len = len(share_bytes)
            length_header = share_len.to_bytes(4, byteorder='big')
            final_share_payload = length_header + share_bytes
            
            binary_string = ''.join([format(b, '08b') for b in final_share_payload])
            
            jpeg_struct = jio.read(carrier_path)
            img_h, img_w = jpeg_struct.coef_arrays[0].shape
            actual_total_blocks = (img_h // 8) * (img_w // 8)
            
            scatter = PathScatterEngine(total_blocks=actual_total_blocks) 
            path_seed = hashlib.sha256((self.master_password + str(index)).encode()).digest()
            prng_path = scatter.generate_block_path(path_seed)

            carrier_filename = os.path.basename(carrier_path)
            output_path = os.path.join(output_dir, f"SHARE_{index+1}_{carrier_filename}")
            
            self.injector.inject_payload(carrier_path, binary_string, prng_path, output_path)
            print(f"  [+] Share {index+1} locked into {carrier_filename}")

        print(f"[+] DISTRIBUTED FORWARD PIPELINE COMPLETE. (Elapsed: {time.time() - start_time:.2f}s)")

    def extract_file_distributed(self, stego_images: list, output_filepath: str):
        print(f"\n[<<<] STARTING DISTRIBUTED REVERSE PIPELINE")
        start_time = time.time()

        recovered_shares_hex = []

        for index, stego_path in enumerate(stego_images):
            jpeg_struct = jio.read(stego_path)
            img_h, img_w = jpeg_struct.coef_arrays[0].shape
            actual_total_blocks = (img_h // 8) * (img_w // 8)
            
            scatter = PathScatterEngine(total_blocks=actual_total_blocks)
            path_seed = hashlib.sha256((self.master_password + str(index)).encode()).digest()
            prng_path = scatter.generate_block_path(path_seed)

            max_bits = actual_total_blocks 
            extracted_bits = self.injector.extract_payload(stego_path, prng_path, max_bits)
            
            header_bits = extracted_bits[:32]
            share_byte_length = int.from_bytes(int(header_bits, 2).to_bytes(4, byteorder='big'), byteorder='big')
            
            target_bit_length = share_byte_length * 8
            share_bits = extracted_bits[32:32 + target_bit_length]
            
            share_bytes = bytearray()
            for i in range(0, len(share_bits), 8):
                byte = share_bits[i:i+8]
                if len(byte) == 8:
                    share_bytes.append(int(byte, 2))
                    
            recovered_shares_hex.append(bytes(share_bytes).hex())
            print(f"  [+] Extracted mathematical share from {os.path.basename(stego_path)}")

        print("  [*] Interpolating polynomials to reconstruct original payload...")
        try:
            reconstructed_hex = secrets.combine(recovered_shares_hex)
            armored_bytes = bytes.fromhex(reconstructed_hex)
        except Exception as e:
            raise ValueError(f"[-] FATAL: Failed to reconstruct shares. Not enough images provided or data corrupted. {e}")
                
        print("  [*] Healing data with Reed-Solomon...")
        healed_encrypted_payload = self.ecc.decode_payload(armored_bytes)
        
        print("  [*] Verifying GCM Tag & Decrypting...")
        raw_data = self.crypto.decrypt_payload(healed_encrypted_payload, self.master_password)
        
        with open(output_filepath, "wb") as f:
            f.write(raw_data)
        
        print(f"[+] DISTRIBUTED REVERSE PIPELINE COMPLETE. Recovered in {time.time() - start_time:.2f}s")
