import os
import sys
import shutil
from typing import List, Tuple

# Dictionary for extension to type of file
exten_to_type: dict = {
    '.nes' : ['NES'],
    '.snes' : ['SNES'],
    '.n64' : ['N64'],
    '.sfc' : ['SNES'],
    '.nds' : ['NDS'],
    '.wbfs' : ['WII'],
    '.ciso' : ['GC'],
    '.gdi' : ['DC'],
    '.cue' : ['SS','PS1'],
    '.dmg' : ['PSP'],
    '.iso' : ['WII','PS1','PS2','DC','GC']
}

# Dictionary for type of folder to sorted folder (within desintation_folder)
type_to_folder: dict = {
    'NES' : 'NES',
    'SNES' : 'SNES',
    'N64' : 'N64',
    'SNES' : 'SNES',
    'NDS' : 'NDS',
    'WII' : 'WII',
    'GC' : 'GC',
    'DC' : 'DC',
    'PSP' : 'PSP',
    'SS' : 'SS',
    'PS1' : 'PS1'
}

# Type of unrecognized types
UNKNOWN: str = "UNKNOWN"

# List of recognized game extensions
game_exten: list = list(exten_to_type.keys())

# List of recognized disk files
disk_based_files = ['.bin','.cue','.gdi']

# Return true if path is a directory
def is_directory(folder_path):
    is_direct = os.path.isdir(folder_path)
    return is_direct

# Return true if path is a file
def is_file(file_path):
    is_fil = os.path.isfile(file_path)
    return is_fil

# Return true if folder is a disk directory
def is_disk_directory(folder_path):
    if is_directory(folder_path):
        for filename in os.listdir(folder_path):
            
            file_extension = get_file_extension(filename)
            
            if file_extension in disk_based_files:
                return True
        
    return False    

# Join any number of paths
def join_paths(*paths):
    joined = os.path.join(*paths)
    return joined

# Return true if path exists
def directory_exists(path):
    exists = os.path.exists(path)
    return exists

# Return file extension
def get_file_extension(file_path):
    file_extension: str = os.path.splitext(file_path.lower())[1]
    return file_extension

# Return file type 
def get_file_type(file_path):
    file_exten: str = get_file_extension(file_path)
    file_type: str = UNKNOWN

    # If path is
    if file_exten in game_exten:
        file_type = exten_to_type[file_exten]

    return file_type

# Returns type of system disk folder belongs to
def get_disk_type(folder_path):
    if is_directory(folder_path):

        # Iterating through each 
        for filename in os.listdir(folder_path):
            file_type = get_file_type(filename)
            
            if file_type != UNKNOWN:
                return file_type
            
    return UNKNOWN

# Compiles and returns a list of paths to game files in the source_folder 
def compile_files(source_folder):
    output_list: list[Tuple[str, list]] = []
    
    # Iterating through each file/dir in source
    for file_name in os.listdir(source_folder):
        file_path = join_paths(source_folder, file_name)

        # If we find a file
        if is_file(file_path):
            file_type = get_file_type(file_name)
            print(file_type)
            if get_file_type(file_name) != "UNKNOWN":
                output_list.append((file_path, file_type))
                print(f"Found {file_name} of type {file_type}")

        # If we find a directory
        elif is_directory(file_path):
            # If folder is a disk-folder
            if is_disk_directory(file_path):
                
                disk_type = get_disk_type(file_path)

                # Add path and type to output
                output_list.append((file_path, disk_type))

                print(f"Found {file_name} of type {disk_type}")

            # If folder is just a folder
            else:
                output_list = output_list + compile_files((file_path))
                print(f"Found {file_name} of type FOLDER.")

        # If element was not recognized as file or dir
        else:
            print("ERROR : CAN'T RECOGNIZE TYPE")

    return output_list 

def move_files_to_destination(files_to_move: list[Tuple[str, list]], destination_folder):
    for file in files_to_move:
        
        file_path = file[0]
        file_type: str
        if len(file[1]) == 1:
            file_type = file[1][0]

        elif len(file[1]) > 1:
            
            while(True):
                print(f"File is of which type?: \n {file[1]} or UNKNOWN?")
                userInput = input(":>> ")

                if userInput in file[1] or userInput == "UNKNOWN":
                    file_type = file[1].index(userInput)
                    break
        else:
            file_type = "UNKNOWN"

        file_type = file[1][0]
        
        ext_folder_path = os.path.join(destination_folder, type_to_folder[file_type])

        if not directory_exists(ext_folder_path):
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
    
    # Ask if all files are okay to put in to the destination folder
    while True:
        print("All OK? (Y/n)\n")
        print('\n'.join(files_to_move))

        response = input("\n:>> ")

        # if yes
        if response.lower() == 'y':
            break
        # if no
        elif response.lower() == 'n':
            response = input("Cancel which file? (FILENAME/all)\n:>> ")
            # cancel all files
            if response.lower() == 'all':
                print("Cancel ALL")
                files_to_move = []
                break
            elif response in files_to_move:
                print(f"Deleting {response}")
                files_to_move.remove(response)
            else:
                print(f"{response} not in files to move / already deleted")
        # if input unrecognized
        else:
            print("ERROR: Bad user input\n")

    # If OK, extract
    move_files_to_destination(files_to_move, destination_folder)

    print("Done!")

if __name__ == "__main__":
    main()
