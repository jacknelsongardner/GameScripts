import os
import sys
import shutil

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
def is_directory(path):
    is_direct = os.path.isdir(path)
    return is_direct

# Return true if path is a file
def is_file(path):
    is_fil = os.path.isfile(path)
    return is_fil

# Return true if path is a game file
def is_game_file(path):
    is_game = False
    if os.path.isfile(path):
        if get_file_type(path) != "UNKNOWN":
            is_game = True
    
    return is_game

def is_game_disk(path):
    if is_directory(path):
        for filename in os.listdir(path):
            print(filename)
            file_extension = get_file_extension(filename)
            print(file_extension)
            if file_extension in disk_based_files:
                return True
        
    return False    

def join_paths(*paths):
    joined = os.path.join(*paths)
    return joined

def directory_exists(path):
    exists = os.path.exists(path)
    return exists

# Return file extension
def get_file_extension(file_path):
    file_extension: str = os.path.splitext(file_path.lower())[1]
    return file_extension

def get_file_type(file_path):
    file_path: str = get_file_extension(file_path)
    file_type: str = "UNKNOWN"

    if file_path in list(exten_to_type.keys()):
        file_type = exten_to_type[file_path]

    return file_type

def get_disk_type(folder_path):
    if is_directory(folder_path):
        for filename in os.listdir(folder_path):
            file_type = get_file_type(filename)
            
            if file_type != "UNKNOWN":
                return file_type
            
    return "UNKNOWN"

def compile_files(source_folder):
    output_list = []
    
    for file_name in os.listdir(source_folder):
        file_path = join_paths(source_folder, file_name)

        if is_file(file_path):
            file_type = get_file_type(file_name)
            print(file_type)
            if get_file_type(file_name) != "UNKNOWN":
                output_list.append((file_path, file_type))
                print(f"Found {file_name} of type {file_type}")

        elif is_directory(file_path):
            if is_game_disk(file_path):
                
                disk_type = get_disk_type(file_path)

                output_list.append((file_path, disk_type))
                print(f"Found {file_name} of type {disk_type}")
  
            else:
                output_list = output_list + compile_files((file_path))
                print(f"Found {file_name} of type FOLDER.")

        else:
            print("nothing found")

    return output_list 

def move_files_to_destination(files_to_move, source_folder, destination_folder):
    for file in files_to_move:
        print(file)
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

        print(file)
        file_type = file[1][0]
        
        print(file_type)
        ext_folder_path = os.path.join(destination_folder, type_to_folder[file_type])

        print(ext_folder_path)

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
        print(f"\n {files_to_move}")

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
