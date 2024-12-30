import os
import numpy as np
from PIL import Image
import shutil
from datetime import datetime

def check_extreme_pixels(image_path, threshold_percentage=5):
    with Image.open(image_path) as img:
        img_array = np.array(img)
    
    total_pixels = img_array.shape[0] * img_array.shape[1]
    
    if img_array.shape[-1] == 4:
        img_array = img_array[:, :, :3]
    
    # Check for pure black (0,0,0)
    pure_black = np.sum(np.all(img_array == [0, 0, 0], axis=-1))
    pure_black_percentage = (pure_black / total_pixels) * 100
    
    # Check for near-black (R,G,B all below 10)
    near_black = np.sum(np.all(img_array < 10, axis=-1))
    near_black_percentage = (near_black / total_pixels) * 100
    
    # Check for pure white (255,255,255)
    pure_white = np.sum(np.all(img_array == [255, 255, 255], axis=-1))
    pure_white_percentage = (pure_white / total_pixels) * 100
    
    # Check for near-white (R,G,B all above 245)
    near_white = np.sum(np.all(img_array > 245, axis=-1))
    near_white_percentage = (near_white / total_pixels) * 100
    
    return {
        'pure_black_percentage': pure_black_percentage,
        'near_black_percentage': near_black_percentage,
        'pure_white_percentage': pure_white_percentage,
        'near_white_percentage': near_white_percentage,
        'has_extreme': (near_black_percentage > threshold_percentage or 
                       near_white_percentage > threshold_percentage)
    }

def process_folder(folder_path):
    print(f"\nStarting scan at {datetime.now().strftime('%H:%M:%S')}")
    print(f"Scanning folder: {folder_path}\n")
    
    png_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
    total_files = len(png_files)
    problem_files = 0
    
    print(f"Found {total_files} PNG files to process\n")
    
    for i, filename in enumerate(png_files, 1):
        image_path = os.path.join(folder_path, filename)
        print(f"Processing {i}/{total_files}: {filename}", end='')
        
        try:
            results = check_extreme_pixels(image_path)
            if results['has_extreme']:
                print(f"\n  Near-black: {results['near_black_percentage']:.1f}%")
                print(f"  Pure black: {results['pure_black_percentage']:.1f}%")
                print(f"  Near-white: {results['near_white_percentage']:.1f}%")
                print(f"  Pure white: {results['pure_white_percentage']:.1f}%")
                problem_files += 1
                
                if not filename.startswith('x-'):
                    new_filename = f'x-{filename}'
                    new_path = os.path.join(folder_path, new_filename)
                    try:
                        shutil.copy2(image_path, new_path)
                        os.remove(image_path)
                        print(f"  Renamed to {new_filename}")
                    except PermissionError:
                        print(f"  Permission denied when renaming")
            else:
                print(" - OK")
                
        except Exception as e:
            print(f"\nError processing {filename}: {e}")
            problem_files += 1

    print(f"\nScan completed at {datetime.now().strftime('%H:%M:%S')}")
    print(f"Total files: {total_files}")
    print(f"Files with issues: {problem_files}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python script.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print("Error: Please provide a valid folder path")
        sys.exit(1)
        
    process_folder(folder_path)
