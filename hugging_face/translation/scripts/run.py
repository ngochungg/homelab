import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.translate import translate_en2vi, translate_vi2en, translate_en2vi_long_text

def main():
    start = time.perf_counter()
    if(len(sys.argv) != 2):
        print("Usage: python run.py <file.txt>")
        sys.exit(1)
    
    file_path = sys.argv[1]

    # Read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Translate the text
    translation = translate_en2vi_long_text(text)

    elapsed = time.perf_counter() - start

    # Print the translation
    print(translation)
    print(f"\nExecution time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()