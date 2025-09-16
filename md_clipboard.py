#!/usr/bin/env python3

import os
import sys
import glob
import subprocess
import argparse


def find_md_files(search_term, search_path="."):
    """
    Find .md files by filename containing the search term.
    
    Args:
        search_term (str): The term to search for in filenames
        search_path (str): The path to search in (default: current directory)
    
    Returns:
        list: List of matching .md file paths
    """
    # Use glob to find all .md files recursively
    pattern = os.path.join(search_path, "**", "*.md")
    all_md_files = glob.glob(pattern, recursive=True)
    
    # Filter files that contain the search term in their filename
    matching_files = []
    for file_path in all_md_files:
        filename = os.path.basename(file_path)
        if search_term.lower() in filename.lower():
            matching_files.append(file_path)
    
    return matching_files


def copy_to_clipboard(content):
    """
    Copy content to clipboard using pbcopy (macOS).
    
    Args:
        content (str): The content to copy to clipboard
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(content.encode('utf-8'))
        return process.returncode == 0
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False


def read_file_content(file_path):
    """
    Read the content of a file.
    
    Args:
        file_path (str): Path to the file to read
        
    Returns:
        str: The content of the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""


def main():
    """Main function to handle command line arguments and execute the script."""
    parser = argparse.ArgumentParser(description="Find .md files and copy contents to clipboard")
    parser.add_argument("search_term", help="Term to search for in .md filenames")
    parser.add_argument("--path", default=".", help="Path to search in (default: current directory)")
    parser.add_argument("--list", action="store_true", help="List matching files without copying")
    
    args = parser.parse_args()
    
    # Find matching .md files
    matching_files = find_md_files(args.search_term, args.path)
    
    if not matching_files:
        print(f"No .md files found containing '{args.search_term}' in filename")
        return
    
    if len(matching_files) > 1:
        print("Multiple files found:")
        for i, file_path in enumerate(matching_files, 1):
            print(f"{i}. {file_path}")
        
        if args.list:
            return
            
        try:
            choice = int(input("Select file number to copy: ")) - 1
            if 0 <= choice < len(matching_files):
                selected_file = matching_files[choice]
            else:
                print("Invalid selection")
                return
        except (ValueError, KeyboardInterrupt):
            print("Invalid input or cancelled")
            return
    else:
        selected_file = matching_files[0]
        if args.list:
            print(f"Found: {selected_file}")
            return
    
    # Read file content
    content = read_file_content(selected_file)
    if not content:
        return
    
    # Add triplet at the end
    content_with_triplet = content + "\nxbx"
    
    # Copy to clipboard
    if copy_to_clipboard(content_with_triplet):
        print(f"Successfully copied content from '{selected_file}' to clipboard (with xbx added)")
        print(f"Content length: {len(content)} characters")
    else:
        print("Failed to copy to clipboard")


if __name__ == "__main__":
    main()