import sys
import os
from pathlib import Path

PROJECT_ROOT = Path("C:/Redmi")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.ssl_preprocessing import run_for_dataset

SEQ_LEN = 30
STRIDE = 5
DATASET_DIR = PROJECT_ROOT / "dataset"
PROCESSED_DIR = DATASET_DIR / "processed"

def main():
    if not DATASET_DIR.exists():
        print(f"Dataset directory {DATASET_DIR} not found.")
        return

    # Find all ssl-* directories
    ssl_dirs = [d for d in DATASET_DIR.iterdir() if d.is_dir() and d.name.startswith("ssl-") and d.name != "processed"]
    
    print(f"Found {len(ssl_dirs)} SSL datasets to process.")
    
    for count, d in enumerate(ssl_dirs, 1):
        ssl_name = d.name
        base_name = ssl_name.replace("-", "_")
        
        # Check if already processed
        expected_output = PROCESSED_DIR / ssl_name / f"{base_name}_sequences.pkl"
        if expected_output.exists():
            print(f"[{count}/{len(ssl_dirs)}] Skipping {ssl_name} - already preprocessed: {expected_output}")
            continue
            
        print(f"[{count}/{len(ssl_dirs)}] Preprocessing {ssl_name}...")
        
        # Set max_num_hands
        max_hands = 1 if ssl_name == "ssl-alphabet-converted" else 2
        
        try:
            output_path = run_for_dataset(
                ssl_name=ssl_name,
                max_num_hands=max_hands,
                seq_len=SEQ_LEN,
                stride=STRIDE,
            )
            print(f"Successfully processed {ssl_name} -> {output_path}")
        except Exception as e:
            print(f"Error processing {ssl_name}: {e}")

if __name__ == "__main__":
    main()
