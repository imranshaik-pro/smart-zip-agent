import os
import zipfile

def select_folder():
    """Ask the user to type the folder path directly in the terminal."""
    print("\n📁 Please enter the full path to the folder containing your files.")
    print("Example: /home/imran/Documents/MyFiles")
    folder_path = input("Folder path: ").strip()
    
    # Remove surrounding quotes if the user pasted them
    folder_path = folder_path.strip('"').strip("'")
    
    # Check if the folder exists
    if not os.path.isdir(folder_path):
        print(f"❌ Error: The folder '{folder_path}' does not exist. Please try again.")
        return select_folder()  # Ask again
    return folder_path

def get_max_size_mb():
    """Ask the user for the maximum ZIP size in MB via terminal input."""
    while True:
        try:
            size_input = input("\n📦 Enter maximum size per ZIP file (in MB, e.g., 100): ")
            if not size_input:
                print("❌ Please enter a number.")
                continue
            size_mb = float(size_input)
            if size_mb <= 0:
                print("❌ Please enter a positive number.")
                continue
            return int(size_mb * 1024 * 1024)  # Convert MB to bytes
        except ValueError:
            print("❌ Invalid input. Please enter a number (e.g., 50).")

def get_all_files(folder):
    """Recursively get all file paths within the folder (excluding subfolders)."""
    all_files = []
    for root_dir, dirs, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root_dir, file)
            rel_path = os.path.relpath(full_path, folder)
            all_files.append((full_path, rel_path))
    return all_files

def pack_files_into_zips(folder, file_list, max_bytes):
    """
    Pack files into multiple ZIP archives using a greedy bin-packing approach.
    Files are sorted by size (largest first) to better utilise space.
    """
    if not file_list:
        print("❌ No files found in the selected folder.")
        return

    # Sort files by size descending (largest first)
    file_list.sort(key=lambda x: os.path.getsize(x[0]), reverse=True)

    # List of bins: each bin is a dict with 'total_size' and list of (full_path, rel_path)
    bins = []

    for full_path, rel_path in file_list:
        file_size = os.path.getsize(full_path)

        # If a single file exceeds the limit, warn and skip it
        if file_size > max_bytes:
            print(f"⚠️ WARNING: File '{rel_path}' is {file_size/(1024*1024):.2f} MB, which exceeds the limit. Skipping it.")
            continue

        placed = False
        # Try to place into an existing bin that has enough room
        for bin in bins:
            if bin['total_size'] + file_size <= max_bytes:
                bin['files'].append((full_path, rel_path))
                bin['total_size'] += file_size
                placed = True
                break

        # If not placed, create a new bin
        if not placed:
            bins.append({
                'total_size': file_size,
                'files': [(full_path, rel_path)]
            })

    # Now create the ZIP files
    if not bins:
        print("❌ No files could be packed (all were too large or no files).")
        return

    # Create a folder named "Zipped_Archives" inside the selected folder to store the ZIPs
    output_folder = os.path.join(folder, "Zipped_Archives")
    os.makedirs(output_folder, exist_ok=True)

    for i, bin in enumerate(bins, start=1):
        zip_filename = os.path.join(output_folder, f"archive_{i}.zip")
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for full_path, rel_path in bin['files']:
                zipf.write(full_path, arcname=rel_path)
        print(f"✅ Created {zip_filename} with {len(bin['files'])} files, total size {bin['total_size']/(1024*1024):.2f} MB")

    print(f"\n🎉 All done! {len(bins)} ZIP archives created in '{output_folder}'.")

def main():
    print("=== Windows AI Smart Zip Agent (Terminal Edition) ===")
    folder = select_folder()
    if not folder:
        print("No folder selected. Exiting.")
        return

    max_bytes = get_max_size_mb()
    if max_bytes is None:
        print("No size entered. Exiting.")
        return

    print(f"\n🔍 Scanning folder: {folder}")
    file_list = get_all_files(folder)
    print(f"📄 Found {len(file_list)} files.")

    pack_files_into_zips(folder, file_list, max_bytes)

if __name__ == "__main__":
    main()
