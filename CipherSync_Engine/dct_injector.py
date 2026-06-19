import jpegio as jio
import numpy as np

class QuantizedDCTInjector:
    def __init__(self):
        # Upgrade: Instead of 1 target, we define a cluster of safe mid-frequencies
        self.target_coords = [(4,4), (4,5), (5,4), (3,5), (5,3), (3,4), (4,3)]

    def inject_payload(self, carrier_path: str, armored_bits: str, block_path: list, output_path: str):
        print(f"[*] Opening {carrier_path} via libjpeg-turbo...")
        jpeg_struct = jio.read(carrier_path)
        y_channel_coeffs = jpeg_struct.coef_arrays[0]
        
        height, width = y_channel_coeffs.shape
        blocks_wide = width // 8
        
        payload_length = len(armored_bits)
        embedded_count = 0
        
        print(f"[*] Injecting {payload_length} bits using Multi-Band PRNG scatter...")
        
        for path_index in block_path:
            if embedded_count >= payload_length:
                break
                
            block_y = (path_index // blocks_wide) * 8
            block_x = (path_index % blocks_wide) * 8
            
            # Upgrade: Try multiple frequencies in the block until we find a safe one
            for (u, v) in self.target_coords:
                coef_val = y_channel_coeffs[block_y + u, block_x + v]
                
                if coef_val != 0 and coef_val != 1 and coef_val != -1:
                    target_bit = int(armored_bits[embedded_count])
                    
                    if target_bit == 0 and coef_val % 2 != 0:
                        coef_val -= 1
                    elif target_bit == 1 and coef_val % 2 == 0:
                        coef_val += 1
                        
                    y_channel_coeffs[block_y + u, block_x + v] = coef_val
                    embedded_count += 1
                    break # Stop after 1 successful embed to keep block noise low

        if embedded_count < payload_length:
            raise ValueError(f"[-] FATAL: Carrier capacity exceeded! (Embedded {embedded_count}/{payload_length} bits). Use a higher resolution or more complex image.")

        print(f"[*] Writing modified DCT matrices to {output_path}...")
        jio.write(jpeg_struct, output_path)
        print("[+] Injection Complete. The data is woven into the frequency domain.")

    def extract_payload(self, stego_path: str, block_path: list, payload_length: int) -> str:
        # We also need to update the extractor to search the same cluster
        jpeg_struct = jio.read(stego_path)
        y_channel_coeffs = jpeg_struct.coef_arrays[0]
        
        height, width = y_channel_coeffs.shape
        blocks_wide = width // 8
        extracted_bits = ""
        
        for path_index in block_path:
            if len(extracted_bits) >= payload_length:
                break
                
            block_y = (path_index // blocks_wide) * 8
            block_x = (path_index % blocks_wide) * 8
            
            for (u, v) in self.target_coords:
                coef_val = y_channel_coeffs[block_y + u, block_x + v]
                if coef_val != 0 and coef_val != 1 and coef_val != -1:
                    extracted_bits += str(abs(coef_val) % 2)
                    break
                
        return extracted_bits
