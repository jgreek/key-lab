import subprocess
import os

class IDEOpener:
    def __init__(self):
        pass
    
    def open_in_cursor(self, folder_path):
        """Open a folder in Cursor IDE"""
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Path does not exist: {folder_path}")
        
        try:
            subprocess.run(['cursor', folder_path], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to open {folder_path} in Cursor: {e}")
    
    def open_in_pycharm(self, folder_path):
        """Open a folder in PyCharm IDE"""
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Path does not exist: {folder_path}")
        
        try:
            subprocess.run(['pycharm', folder_path], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to open {folder_path} in PyCharm: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python ide_opener.py <ide> <folder_path>")
        print("  ide: cursor or pycharm")
        sys.exit(1)
    
    ide = sys.argv[1].lower()
    folder_path = sys.argv[2]
    
    opener = IDEOpener()
    
    if ide == 'cursor':
        opener.open_in_cursor(folder_path)
    elif ide == 'pycharm':
        opener.open_in_pycharm(folder_path)
    else:
        print(f"Unsupported IDE: {ide}")
        sys.exit(1)