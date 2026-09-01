import os
import re

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False
        
    new_content = content
    # Replace AlphaFund variants
    new_content = re.sub(r'AlphaFund', 'InsightEdge Research', new_content)
    new_content = re.sub(r'ALPHAFUND', 'INSIGHTEDGE RESEARCH', new_content)
    new_content = re.sub(r'Alpha Fund', 'InsightEdge Research', new_content, flags=re.IGNORECASE)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    root_dir = "."
    exclude_dirs = {'.git', 'node_modules', '.next', '__pycache__', 'venv', '.venv'}
    exclude_exts = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.pyc'}
    
    count = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # modify dirnames in-place to exclude directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in exclude_exts or filename == 'rename_script.py':
                continue
                
            filepath = os.path.join(dirpath, filename)
            if replace_in_file(filepath):
                print(f"Updated: {filepath}")
                count += 1
                
    print(f"Done! Updated {count} files.")

if __name__ == '__main__':
    main()
