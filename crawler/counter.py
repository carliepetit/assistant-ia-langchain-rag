import os

# Set the directory to search (current directory by default)
base_directory = os.getcwd()  # Gets the current working directory

total_md_files = 0

# Walk through all folders in the base directory
for root, dirs, files in os.walk(base_directory):
    # Count .md files in the current folder
    md_files = [f for f in files if f.endswith('.md')]
    folder_count = len(md_files)
    total_md_files += folder_count
    
    if folder_count > 0:
        print(f"Folder: {root} - Found {folder_count} .md files")

# Print the total
print(f"\nTotal number of .md files across all folders: {total_md_files}")