import os
import sys
import shutil

exten_to_type = {
    '.nes' : 'NES',
    '.snes' : 'SNES',
    '.n64' : 'N64',
    '.sfc' : 'SNES',
    '.nds' : 'NDS',
    '.wbfs' : 'WII',
    '.ciso' : 'GC',
    '.gdi' : 'DC'
}

acceptable_extentions = ['.nes','.snes','.n64','.sfc','.nds','.cue','.gdi']

def is_directory(path):

    directory_path = os.path.isdir(path)
    return directory_path

def get_file_extension(file_path):

    file_extension = os.path.splitext(file_path.lower())[1]
    return file_extension

def get_file_type(file_path):

    file_extension = get_file_extension(file_path)

    if file_extension in exten_to_type.keys:
        file_type = exten_to_type[file_extension]
    else:
        file_type = "UNKNOWN"
        
    return file_type

def check_file_extension(file_path):

    file_extension = get_file_extension(file_path)
    # Check if the extension is in the allowed_extensions dictionary
    if file_extension in acceptable_extentions:
        print(f"{file_path} is of {file_extension} type")  
        return True
    else:
        print(f"{file_path} is of UNKNOWN type")  
        return False

def check_folder_type(folder_path):

    if os.is_directory(folder_path):
        for childfile in os.listdir(os.path.join(folder_path, childfile)):
            if get_file_extension(childfile) in disk_extensions:   
                print(f"{folder_path} is of DISK FOLDER type")
                return True


def compile_files(source_folder):
    output_list = []

    for filename in os.listdir(source_folder):
        if check_file_extension(filename) or check_folder_type(filename):
            output_list.append(filename)

    return output_list 

def move_files_to_destination(source_files, source_folder, destination_folder):
    for filename in source_files:

        file_path = os.path.join(source_folder, filename)

        ext_folder_path = os.path.join(destination_folder, exten_to_type[get_file_extension(file_path)])

        if not os.path.exists(ext_folder_path):
            os.makedirs(ext_folder_path)
        
        shutil.move(file_path, ext_folder_path)

        print(f"{file_path} moved to {ext_folder_path}")

def main():
    # Check if there are exactly three command-line arguments (including the script name)
    if len(sys.argv) != 3:
        print("Usage: python script.py source_folder destination_folder")
        return

    # Check if there are at least three command-line arguments (including the script name)
    if len(sys.argv) != 3:
        print("Usage: python script.py source_folder destination_folder")
        return
    
    # Access command-line arguments
    source_folder = os.path.join(os.path.expanduser("~"), sys.argv[1])
    destination_folder = os.path.join(os.path.expanduser("~"), sys.argv[2])

    print(f"Source Folder: {source_folder}")
    print(f"Destination Folder: {destination_folder}")
    
    # Compile files that are 7z in source folder
    files_to_move = compile_files(source_folder)
    
    # Ask if all files are okay to unzip to the destination folder
    while True:
        print("All OK? (Y/n)\n")
        print('\n'.join(files_to_move))

        response = input("\n:>> ")

        if response.lower() == 'y':
            break
        elif response.lower() == 'n':
            response = input("Delete which file? (FILENAME/all)\n:>> ")

            if response.lower() == 'all':
                print("Deleting ALL")
                files_to_move = []
                break
            elif response in files_to_move:
                print(f"Deleting {response}")
                files_to_move.remove(response)
        else:
            print("ERROR: Bad user input\n")

    # If OK, extract
    move_files_to_destination(files_to_move, source_folder, destination_folder)

    print("Done!")

if __name__ == "__main__":
    main()
