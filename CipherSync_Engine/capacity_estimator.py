import cv2
import os

class CapacityEstimator:
    def __init__(self, block_size=8):
        self.block_size = block_size

    def analyze_carrier(self, image_path: str, bits_per_block: int = 2, use_chroma: bool = False) -> dict:
        """
        Analyzes a single image file to determine its safe steganographic capacity.
        
        :param image_path: Path to the target carrier image
        :param bits_per_block: Number of bits hidden in each 8x8 block (Recommended: 1-3)
        :param use_chroma: If True, includes Cr and Cb channels (Increases space, increases risk)
        :return: Dictionary containing structural and capacity metrics
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Target image not found at: {image_path}")

        # Read image dimensions without loading full matrix into memory if possible
        img = cv2.imread(image_path)
        height, width, channels = img.shape

        # Calculate exact number of non-overlapping 8x8 blocks
        blocks_high = height // self.block_size
        blocks_wide = width // self.block_size
        total_blocks = blocks_high * blocks_wide

        # Determine active channels for embedding
        active_channels = 3 if use_chroma else 1

        # Calculate capacities
        total_bits = total_blocks * bits_per_block * active_channels
        total_bytes = total_bits // 8
        capacity_kb = total_bytes / 1024

        return {
            "filename": os.path.basename(image_path),
            "resolution": f"{width}x{height}",
            "total_pixels": width * height,
            "total_blocks": total_blocks,
            "bits_per_block": bits_per_block,
            "channels_utilized": "Y (Luminance Only)" if active_channels == 1 else "Y, Cr, Cb (Full Spectrum)",
            "safe_capacity_bytes": total_bytes,
            "safe_capacity_kb": round(capacity_kb, 2),
            "safe_capacity_mb": round(capacity_kb / 1024, 2)
        }

# ==========================================
# EXECUTION ROUTINE
# ==========================================
if __name__ == "__main__":
    # Example usage: Replace with a path to one of your local images
    estimator = CapacityEstimator()
    
    print("[*] Running steganographic profile estimation...")
    try:
        # Dummy path for demonstration structure
        sample_image = "carrier_test.jpg"
        
        # For testing purposes, let's look at theoretical limits for standard 1080p
        print("\n[+] Theoretical Safe Metrics for a Standard 1080p Carrier (1920x1080):")
        blocks = (1920 // 8) * (1080 // 8)
        bytes_capacity = (blocks * 2) // 8 # 2 bits per block
        print(f"    -> Total 8x8 Blocks: {blocks}")
        print(f"    -> Safe Payload Space: {bytes_capacity / 1024:.2f} KB")
        
    except Exception as e:
        print(f"[-] Error parsing image: {e}")
