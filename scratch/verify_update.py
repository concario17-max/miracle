import os
import json

def verify_json():
    path = "public/bodhi-commentary.json"
    if not os.path.exists(path):
        print("Error: public/bodhi-commentary.json does not exist!")
        return False
        
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return False
        
    print(f"JSON validation: Success. Total keys: {len(data)}")
    
    # Check a few specific keys
    test_keys = [
        "miracle.1.1", "miracle.1.50",
        "miracle.2.61", "miracle.2.80",
        "miracle.3.91", "miracle.3.110",
        "miracle.4.121", "miracle.4.140",
        "miracle.5.151", "miracle.5.170",
        "miracle.6.181", "miracle.6.200",
        "miracle.7.221", "miracle.7.230",
        "miracle.8.231", "miracle.8.240",
        "miracle.9.241", "miracle.9.250",
        "miracle.10.251", "miracle.10.260",
        "miracle.11.261", "miracle.11.270",
        "miracle.12.271", "miracle.12.280",
        "miracle.13.281", "miracle.13.290",
        "miracle.14.291", "miracle.14.300"
    ]
    missing = []
    for k in test_keys:
        if k not in data:
            missing.append(k)
            
    if missing:
        print(f"Warning: Expected keys missing: {missing}")
    else:
        print("All target check keys are present in the JSON.")
        
    # Check that miracle.4.125 is indeed present (it was updated previously)
    if "miracle.4.125" not in data:
        print("Warning: miracle.4.125 was not found in JSON.")
    else:
        print("miracle.4.125 is in JSON (as expected).")
        
    return True

def verify_comic_folders():
    comic_root = "src/assets/learning-comic"
    
    for ch in range(1, 15):
        ch_path = os.path.join(comic_root, f"chapter-{ch}")
        if not os.path.exists(ch_path):
            print(f"Error: Directory {ch_path} does not exist!")
            continue
            
        files = [f for f in os.listdir(ch_path) if f.endswith(".webp")]
        print(f"Chapter-{ch} folder: {len(files)} files.")
        
        # Print a few examples
        if files:
            print(f"  Examples in chapter-{ch}: {sorted(files)[:3]} ... {sorted(files)[-2:]}")

def main():
    print("=== Verification Starting ===")
    json_ok = verify_json()
    print("\n=== Checking Comic Folders ===")
    verify_comic_folders()
    
if __name__ == "__main__":
    main()

