import os

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()
    
def get_full_path(relative_path):
    base_dir = os.getenv('BASE_DIR', default=os.getcwd())
    return os.path.join(base_dir, relative_path)