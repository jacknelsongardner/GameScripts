import os
import py7zr
import sys
import zipfile

def compile_zip_files(source_folder):
    output_list = []

    for filename in os.listdir(source_folder):
        if filename.endswith(".7z") or filename.endswith(".zip"):
            output_list.append(filename)
        
    
    return output_list

def extract_and_delete_zip_files(source_files, source_folder, destination_folder):
    for filename in source_files:
        file_path = os.path.join(source_folder, filename)

        # Check if the file is a 7z archive
        if filename.endswith(".7z"):
            with py7zr.SevenZipFile(file_path, mode='r') as z:
                # Extract to the destination path
                z.extractall(destination_folder)
                print(f"Extracted {filename} to {destination_folder}")

            # Delete the 7z file after extraction
            os.remove(file_path)
            print(f"Deleted {filename}")
        
        # Check if the file is a zip archive
        if filename.endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as z:
                z.extractall(destination_folder)
                print(f"Extracted {filename} to {destination_folder}")

            # Delete the 7z file after extraction
            os.remove(file_path)
            print(f"Deleted {filename}")

def main():
    # Check if there are at least three command-line arguments (including the script name)
    if len(sys.argv) != 3:
        print("Usage: python script.py source_folder destination_folder")
        return

    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

    # Access command-line arguments
    source_folder = os.path.join(os.path.expanduser("~"), sys.argv[1])
    destination_folder = os.path.join(os.path.expanduser("~"), sys.argv[2])

    print(f"Source Folder: {source_folder}")
    print(f"Destination Folder: {destination_folder}")
    
    # Compile files that are 7z in source folder
    zip_files = compile_zip_files(source_folder)
    
    # Ask if all files are okay to unzip to the destination folder
    while True:
        print("All OK? (Y/n)\n")
        print('\n'.join(zip_files))

        response = input("\n:>> ")

        if response.lower() == 'y':
            break
        elif response.lower() == 'n':
            response = input("Delete which file? (FILENAME/all)\n:>> ")

            if response.lower() == 'all':
                print("Deleting ALL")
                zip_files = []
                break
            elif response in zip_files:
                print(f"Deleting {response}")
                zip_files.remove(response)
        else:
            print("ERROR: Bad user input\n")

    # If OK, extract
    extract_and_delete_zip_files(zip_files, source_folder, destination_folder)

    print("Done!")

if __name__ == "__main__":
    main()
