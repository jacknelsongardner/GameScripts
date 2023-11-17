import os
import sys
import shutil

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
    '.dmg' : ['PSP']
}

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
    'UNKNOWN' : 'UNRESOLVED'
}


disc_based_files = ['.bin','.cue','.gdi']

# Return whether path is a directory
def is_directory(path):
    return os.path.isdir(path)
    
def is_file(path):
    return os.path.isfile(path)

def is_game_disk(path):
    if is_directory(path):
        for filename in path:
            file_extension = get_file_extension(filename)
            file_type = get_file_type(file_extension)

            if file_type in disc_based_files:
                return True
        
    return False    

# Return file extension
def get_file_extension(file_path):
    file_extension: str = os.path.splitext(file_path.lower())[1]
    return file_extension


def get_file_type(file_extension):

    file_type: str = "UNKNOWN"

    if file_extension in exten_to_type.keys:
        file_type = exten_to_type[file_extension]

    return file_type

def get_disk_type(folder_path):
    if is_directory(folder_path):
        for filename in folder_path:
            file_extension = get_file_extension(filename)
            file_type = get_file_type(file_extension)

            if file_type != "UNKNOWN":
                return file_type
            
    return "UNKNOWN"

def compile_files(source_folder):
    output_list = []

    for path in os.listdir(source_folder):
        
        if is_file(path):
            output_list.append(path,get_file_type(path))
        elif is_directory(path):
            
            if is_game_disk(path):
                output_list.append(path,get_disk_type(path))
            else:
                output_list = output_list + compile_files(path)

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
