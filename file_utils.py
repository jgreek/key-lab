#!/usr/bin/env python3
"""
Mac-only file utilities for keystroke commander
Usage: 
  python file_utils.py open <directory> [count] [file_extensions...]
  python file_utils.py organize <source_dir> <destination_dir> [--copy | --replace]
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime


def get_last_files(directory, count=1, extensions=None):
    """
    Get the last x files from a directory sorted by modification time
    
    Args:
        directory (str): Directory path to search
        count (int): Number of files to return (default 1)
        extensions (list): List of file extensions to filter by (optional)
    
    Returns:
        list: List of file paths sorted by modification time (newest first)
    """
    directory = Path(directory)
    
    if not directory.exists() or not directory.is_dir():
        print(f"Error: Directory '{directory}' does not exist or is not a directory")
        return []
    
    # Get all files in directory
    files = []
    for file_path in directory.iterdir():
        if file_path.is_file():
            # Filter by extensions if specified
            if extensions:
                if file_path.suffix.lower() in [ext.lower() for ext in extensions]:
                    files.append(file_path)
            else:
                files.append(file_path)
    
    if not files:
        print(f"No files found in directory '{directory}'")
        return []
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Return the requested number of files
    return files[:count]


def open_file(file_path):
    """Open a file using macOS 'open' command"""
    try:
        subprocess.run(["open", str(file_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error opening file '{file_path}': {e}")
        return False


def get_most_recent_file_time(directory_path):
    """
    Get the modification time of the most recent file in a directory (recursive)
    
    Args:
        directory_path (Path): Directory to search
        
    Returns:
        float: Most recent modification time, or 0 if no files found
    """
    try:
        files = [f for f in directory_path.rglob('*') if f.is_file()]
        if not files:
            return 0
        
        # Find the most recent file
        most_recent_time = max(f.stat().st_mtime for f in files)
        return most_recent_time
    except Exception:
        return 0


def organize_files_by_date(source_dir, destination_dir, copy_files=False):
    """
    Organize files and directories from source_dir into destination_dir/yyyy/mm structure
    based on last modified date. Directories are moved based on their most recent file.
    
    Args:
        source_dir (str): Source directory containing files and directories to organize
        destination_dir (str): Destination directory for organized items
        copy_files (bool): If True, copy items; if False, move items (DEFAULT)
    
    Returns:
        dict: Summary of organized items
    """
    source_path = Path(source_dir)
    dest_path = Path(destination_dir)
    
    if not source_path.exists() or not source_path.is_dir():
        print(f"Error: Source directory '{source_path}' does not exist or is not a directory")
        return {}
    
    # Get all files and directories in source directory (first level only)
    items = [item for item in source_path.iterdir()]
    
    if not items:
        print(f"No items found in source directory '{source_path}'")
        return {}
    
    # Organize files and directories by date
    organized = {}
    operation = "Copying" if copy_files else "Moving"
    
    print(f"{operation} {len(items)} items from '{source_path}' to '{dest_path}'")
    
    for item_path in items:
        try:
            # Determine modification time based on item type
            if item_path.is_file():
                # For files, use their modification time
                mod_time_timestamp = item_path.stat().st_mtime
                item_type = "file"
            elif item_path.is_dir():
                # For directories, use the most recent file within the directory
                mod_time_timestamp = get_most_recent_file_time(item_path)
                if mod_time_timestamp == 0:
                    print(f"  - {item_path.name} (directory): No files found, skipping")
                    continue
                item_type = "directory"
            else:
                # Skip other types (symlinks, etc.)
                continue
            
            mod_time = datetime.fromtimestamp(mod_time_timestamp)
            year = mod_time.year
            month = f"{mod_time.month:02d}"
            
            # Create destination directory structure
            year_month_dir = dest_path / str(year) / month
            year_month_dir.mkdir(parents=True, exist_ok=True)
            
            # Destination path
            dest_item = year_month_dir / item_path.name
            
            # Handle name conflicts
            counter = 1
            original_dest = dest_item
            while dest_item.exists():
                if item_path.is_file():
                    stem = original_dest.stem
                    suffix = original_dest.suffix
                    dest_item = year_month_dir / f"{stem}_{counter}{suffix}"
                else:
                    dest_item = year_month_dir / f"{original_dest.name}_{counter}"
                counter += 1
            
            # Copy or move the item
            if copy_files:
                if item_path.is_file():
                    shutil.copy2(item_path, dest_item)
                else:
                    shutil.copytree(item_path, dest_item)
            else:
                shutil.move(str(item_path), str(dest_item))
            
            # Track organized items
            date_key = f"{year}/{month}"
            if date_key not in organized:
                organized[date_key] = []
            organized[date_key].append(item_path.name)
            
            # Show item and its destination
            print(f"  - {item_path.name} ({item_type}) -> {year}/{month}/")
            
        except Exception as e:
            print(f"Error processing item '{item_path.name}': {e}")
    
    # Print summary
    print(f"\nOrganization complete!")
    print(f"Items organized by date:")
    for date_key, items in sorted(organized.items()):
        print(f"  {date_key}: {len(items)} items")
    
    return organized


def main():
    """Main function to handle command line arguments and operations"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python file_utils.py open <directory> [count] [file_extensions...]")
        print("  python file_utils.py organize <source_dir> <destination_dir> [--copy | --replace]")
        print("")
        print("Examples:")
        print("  python file_utils.py open /Users/john.greek/Screenshots")
        print("  python file_utils.py open /Users/john.greek/Screenshots 3")
        print("  python file_utils.py organize /Users/john.greek/Downloads /Users/john.greek/OrganizedFiles")
        print("  python file_utils.py organize /Users/john.greek/Downloads /Users/john.greek/OrganizedFiles --copy")
        print("  python file_utils.py organize /Users/john.greek/Downloads /Users/john.greek/OrganizedFiles --replace")
        print("")
        print("Options:")
        print("  --copy     Copy files to destination (originals remain in source)")
        print("  --replace  Move files to destination (DEFAULT - originals are moved)")
        print("")
        print("Note: organize command processes files and directories. Directories are moved")
        print("      based on the most recent file within them.")
        sys.exit(1)
    
    operation = sys.argv[1].lower()
    
    if operation == "open":
        handle_open_operation(sys.argv[2:])
    elif operation == "organize":
        handle_organize_operation(sys.argv[2:])
    else:
        print(f"Error: Unknown operation '{operation}'")
        print("Valid operations: open, organize")
        sys.exit(1)


def handle_open_operation(args):
    """Handle the 'open' operation"""
    if len(args) < 1:
        print("Error: 'open' operation requires a directory")
        sys.exit(1)
    
    directory = args[0]
    count = 1
    extensions = None
    
    # Parse count if provided
    if len(args) > 1:
        try:
            count = int(args[1])
        except ValueError:
            print(f"Error: Count must be a number, got '{args[1]}'")
            sys.exit(1)
    
    # Parse extensions if provided
    if len(args) > 2:
        extensions = args[2:]
        # Ensure extensions start with dot
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    
    # Get the last files
    last_files = get_last_files(directory, count, extensions)
    
    if not last_files:
        sys.exit(1)
    
    # Open each file
    print(f"Opening {len(last_files)} file(s) from '{directory}':")
    success_count = 0
    
    for file_path in last_files:
        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        print(f"  - {file_path.name} (modified: {file_time.strftime('%Y-%m-%d %H:%M:%S')})")
        
        if open_file(file_path):
            success_count += 1
    
    print(f"Successfully opened {success_count} out of {len(last_files)} files")


def handle_organize_operation(args):
    """Handle the 'organize' operation"""
    if len(args) < 2:
        print("Error: 'organize' operation requires source_dir and destination_dir")
        sys.exit(1)
    
    source_dir = args[0]
    destination_dir = args[1]
    
    # Default behavior is replace (move files)
    copy_files = False
    
    if "--copy" in args:
        copy_files = True
    elif "--replace" in args:
        copy_files = False
    # If no flag specified, default to replace (move files)
    
    organize_files_by_date(source_dir, destination_dir, copy_files)


if __name__ == "__main__":
    main() 