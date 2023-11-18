import os
import sys
import shutil
from typing import List, Tuple

import queue as q
import queue

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
    '.iso' : ['WII','PS1','PS2','DC','GC'],
    '.sms' : ['SMS'],
    '.md' : ['SG'],
    '.gb' : ['GB'],
    '.gbc' : ['GBC'],
    '.gba' : ['GBA'],
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
    'PS1' : 'PS1',
    'SMS' : 'SMS',
    'SG' : 'SG',
    'GBC' : 'GBC',
    'GB' : 'GB',
    'GBA' : 'GBA',
}

# Unknown type label
UNKNOWN: str = "UNKNOWN"

# Log labels
ERROR: str = "ERROR: "
LOG: str = "LOG: "
COMMAND: str = "COMMND: "
QUESTION: str = "QUESTION: "

# Command labels
ENDWAIT: str = "ENDWAIT"

# Queue for responses and/or requests
reportQ: queue = q.Queue()

# Queue for commands
commandQ: queue = q.Queue()

# List of recognized game extensions
game_exten: list = list(exten_to_type.keys())

# List of recognized disk files
disk_based_files = ['.bin','.cue','.gdi']


# Read commandQ
def read_command() -> str:
    return commandQ.read()

# Write to commandQ
def write_command(command: str) -> None:
    commandQ.put(command)

# Read reportQ
def read_report() -> str:
    return commandQ.read()

# Write to reportQ
def write_report(command: str) -> None:
    commandQ.put(command)   

def await_report() -> None:
    while reportQ.Empty:
        pass 

def await_command() -> None:
    while commandQ.Empty:
        pass 
 
# Return true if path is a directory
def is_directory(folder_path: str) -> bool:
    is_direct = os.path.isdir(folder_path)
    return is_direct

# Return true if path is a file
def is_file(file_path: str) -> bool:
    is_fil = os.path.isfile(file_path)
    return is_fil

# Return true if folder is a disk directory
def is_disk_directory(folder_path: str) -> bool:
    if is_directory(folder_path):
        for filename in os.listdir(folder_path):
            
            file_extension = get_file_extension(filename)
            
            if file_extension in disk_based_files:
                return True
        
    return False    

def get_entry_name(entry_path):
    entry_name = os.path.basename(entry_path)
    return entry_name

# Join any number of paths
def join_paths(*paths: str) -> str:
    joined = os.path.join(*paths)
    return joined

# Return true if path exists
def path_exists(path: str) -> bool:
    exists = os.path.exists(path)
    return exists

# Return file extension
def get_file_extension(file_path: str) -> str:
    file_extension: str = os.path.splitext(file_path.lower())[1]
    return file_extension

# Return file type 
def get_file_type(file_path: str) -> str:
    file_exten: str = get_file_extension(file_path)
    file_type: str = UNKNOWN

    # If path is
    if file_exten in game_exten:
        file_type = exten_to_type[file_exten]

    return file_type

# Returns type of system disk folder belongs to
def get_disk_type(folder_path: str) -> str:
    if is_directory(folder_path):

        # Iterating through each 
        for filename in os.listdir(folder_path):
            file_type = get_file_type(filename)
            
            if file_type != UNKNOWN:
                return file_type
            
    return UNKNOWN

# Compiles and returns a list of paths to game files in the source_folder 
def compile_files(source_folder: str) -> list[Tuple[str, list]]:
    output_list: list[Tuple[str, list]] = []
    
    # Iterating through each file/dir in source
    for file_name in os.listdir(source_folder):
        file_path = join_paths(source_folder, file_name)

        # If we find a file
        if is_file(file_path):
            file_type = get_file_type(file_name)
            
            if get_file_type(file_name) != "UNKNOWN":
                output_list.append((file_path, file_type))
                
                write_report(f"Found {file_name} of type {file_type}")

        # If we find a directory
        elif is_directory(file_path):
            # If folder is a disk-folder
            if is_disk_directory(file_path):
                
                disk_type = get_disk_type(file_path)

                # Add path and type to output
                output_list.append((file_path, disk_type))

                write_report(f"{LOG} Found {file_name} of type {disk_type}")

            # If folder is just a folder
            else:
                output_list = output_list + compile_files((file_path))
                write_report(f"{LOG} Found {file_name} of type FOLDER.")

        # If element was not recognized as file or dir
        else:
            write_report(f"{ERROR} CAN'T RECOGNIZE TYPE")

    return output_list 

def move_files_to_destination(files_to_move: list[Tuple[str, list]], destination_folder: str) -> None:
    for file in files_to_move:
        file_path = file[0]

        file_type: str

        # If we have one argument for type
        if len(file[1]) == 1:
            file_type = file[1][0]
        # If more than one arguments for type
        elif len(file[1]) > 1:
            
            while(True):
                # Ask user which type
                write_report(f"QUESTION: File is of which type?: \n {file[1]} or UNKNOWN?")
                await_command()

                userInput = read_command()

                # Get user input on which type
                if userInput in file[1] or userInput == "UNKNOWN":
                    file_type = file[1].index(userInput)
                    break
        else:
            file_type = "UNKNOWN"

        # Get filetype from the input tuple
        file_type = file[1][0]
        
        ext_folder_path = os.path.join(destination_folder, type_to_folder[file_type])

        # Creating sorting directory if not already there
        if not path_exists(ext_folder_path):
            os.makedirs(ext_folder_path)
        
        # Moving files to destination
        if not path_exists(os.path.join(ext_folder_path, get_entry_name(file_path))):
            shutil.move(file_path, ext_folder_path)
            print(f"{get_entry_name(file_path)} moved to {destination_folder}")
        else:
            print((f"{get_entry_name(file_path)} already exists in {destination_folder}"))

            # Ask if user wants to replace file in destination directory
            while(True):
                print("Replace? Y/n")
                user_input = input(":>>")
                
                if user_input.lower() == 'y':
                    print(user_input)

                    os.remove(join_paths(ext_folder_path,get_entry_name(file_path)))
                    print("Deleted original file")

                    shutil.move(file_path, ext_folder_path)
                    print(f"{get_entry_name(file_path)} moved to {destination_folder}")
                    break
                else:
                    print(user_input)
                    print("Cancelled file move")
                    break

def main() -> None:
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
        # printint all files found for aproval by user
        print("All OK? (Y/n)\n")
        for elem in files_to_move:
            print(elem)

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
