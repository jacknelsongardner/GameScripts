import os
import sys
import shutil
from typing import List, Tuple

import queue as q
import queue

from threading import Thread
from multiprocessing import Process

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
    '.z64' : ['N64'],
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
COMMAND: str = "COMMAND: "
QUESTION: str = "QUESTION: "
CHOICE: str = "CHOICE: "

# Command labels
ENDWAIT: str = "ENDWAIT"

# Yes and No labels
YES: str = "Yes"
NO: str = "No"

# Queue for responses and/or requests
reportQ: queue = q.Queue()

# Queue for commands
commandQ: queue = q.Queue()

# List of recognized game extensions
game_exten: list = list(exten_to_type.keys())

# List of recognized disk files
disk_based_files = ['.bin','.cue','.gdi']


# Rename file in desired directory
def rename_file(old_path, new_name):
    # Extract the directory and file extension
    directory, filename = os.path.split(old_path)
    extension = get_file_extension(old_path)

    # Create the new path with the new name and the original directory
    new_path = os.path.join(directory, new_name + extension)
    os.rename(old_path, new_path)

# Returns renamed file heading but does not create it
def get_renamed_path(old_path, new_name):
    # Extract the directory and file extension
    directory, filename = os.path.split(old_path)
    extension = get_file_extension(old_path)

    # Create the new path with the new name and the original directory
    new_path = os.path.join(directory, new_name + extension)
    return new_path

# Read commandQ
def read_command() -> str:
    return commandQ.get()

# Write to commandQ
def write_command(command: str) -> None:
    commandQ.put(command)

# Read reportQ
def read_report() -> str:
    return commandQ.get()

# Write to reportQ
def write_report(command: str) -> None:
    commandQ.put(command)   

def await_report() -> None:
    while reportQ.empty():
    
        pass 

def await_command() -> None:
    while commandQ.empty():
        
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

# types list of files and returns tuple list with path and type
def type_files(paths_to_type):
    output_list: list[Tuple[str, list]] = []
    
    # Iterating through each file/dir in source
    for file_path in paths_to_type:

        # If we find a file
        if is_file(file_path):
            file_type = get_file_type(file_path)
            
            if get_file_type(file_path) != "UNKNOWN":
                output_list.append((file_path, file_type))
                
                write_report(f"{LOG} Found {file_path} of type {file_type}")

        # If we find a directory
        elif is_directory(file_path):
            # If folder is a disk-folder
            if is_disk_directory(file_path):
                
                disk_type = get_disk_type(file_path)

                # Add path and type to output
                output_list.append((file_path, disk_type))

                write_report(f"{LOG} Found {file_path} of type {disk_type}")

            # If folder is just a folder
            else:
                output_list = output_list + compile_files((file_path))
                write_report(f"{LOG} Found {file_path} of type FOLDER.")

        # If element was not recognized as file or dir
        else:
            write_report(f"{ERROR} CAN'T RECOGNIZE TYPE")

    return output_list 

# Return whether more than one type is available for selected tuple
def more_than_one_type(types: tuple[str,list]):
    if len(types) > 1:
        return True
    else:
        return False

# compile only file directories without returning types
def compile_files_dir(source_folder: str) -> list[str]:
    output_list: list = []
    
    # Iterating through each file/dir in source
    for file_name in os.listdir(source_folder):
        file_path = join_paths(source_folder, file_name)

        # If we find a file
        if is_file(file_path):
            file_type = get_file_type(file_name)
            
            if get_file_type(file_name) != "UNKNOWN":
                output_list.append(file_path)
                
                write_report(f"{LOG} Found {file_name} of type {file_type}")

        # If we find a directory
        elif is_directory(file_path):
            # If folder is a disk-folder
            if is_disk_directory(file_path):
                
                disk_type = get_disk_type(file_path)

                # Add path and type to output
                output_list.append(file_path)

                write_report(f"{LOG} Found {file_name} of type {disk_type}")

            # If folder is just a folder
            else:
                output_list = output_list + compile_files_dir((file_path))
                write_report(f"{LOG} Found {file_name} of type FOLDER.")

        # If element was not recognized as file or dir
        else:
            write_report(f"{ERROR} CAN'T RECOGNIZE TYPE")

    return output_list


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
                
                write_report(f"{LOG} Found {file_name} of type {file_type}")

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
             
            while True:
                # Asking user which type and giving choices
                print(f"{CHOICE} File is of which type?: \n {file[1]} or {UNKNOWN}?")
                print(file[1] + [UNKNOWN])

                userInput = input(":>>")
                 
                # Get user input on which type
                if userInput in file[1] or userInput == UNKNOWN:
                    file_type = file[1].index(userInput)
                    break
        else:
            file_type = UNKNOWN

        # Get filetype from the input tuple
        file_type = file[1][0]
        
        ext_folder_path = os.path.join(destination_folder, type_to_folder[file_type])

        # Creating sorting directory if not already there
        if not path_exists(ext_folder_path):
            os.makedirs(ext_folder_path)
         
        # Moving files to destination
        file_name = get_entry_name(file_path)

        if not path_exists(os.path.join(ext_folder_path, file_name)):
            shutil.move(file_path, ext_folder_path)
            write_report(f"{LOG} {file_name} moved to {destination_folder}")
        else:
            write_report(f"{LOG} {file_name} already exists in {destination_folder} \n Operation cancelled")

def main() -> None:
    # Check if there are exactly three command-line arguments (including the script name)
    if len(sys.argv) != 3:
        print("Usage: python script.py source_folder destination_folder")
        return
    
    # Access command-line arguments
    source_folder = os.path.join(os.path.expanduser("~"), sys.argv[1])
    destination_folder = os.path.join(os.path.expanduser("~"), sys.argv[2])

    print(f"Source Folder: {source_folder}")
    print(f"Destination Folder: {destination_folder}")
    
    files_to_move = compile_files(source_folder)
    
    while not reportQ.empty():
        report = reportQ.get()
        print(report)

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
                print(f"{response} not in files to move / already cancelled")
        # if input unrecognized
        else:
            print("ERROR: Bad user input\n")

    # Check each element to make sure a single destination is asked for
    for file in files_to_move: 
        file_name: str = get_entry_name(file[0])

        # If we have more than one argument for type
        if len(file[1]) > 1:
             
            while True:
                # Asking user which type and giving choices
                print(f"{CHOICE} {file} is of which type?: \n {file[1]} or {UNKNOWN}?")
                print(file[1] + [UNKNOWN])

                userInput = input(":>> ")
                 
                # Get user input on which type
                if userInput in file[1] or userInput == UNKNOWN:
                    file = file[0], file[1].index(userInput)
                    break
    
    # Check each element to make sure they don't have elements that already exist
    for file in files_to_move:
        
        while(True):
            file_path = file[0]
            type_folder = type_to_folder[file[1][0]]
            file_name = get_entry_name(file[0])

            print(file_path)
            print(file_name)


            if path_exists(os.path.join(destination_folder, type_folder, file_name)):
                print(346)
                print((f"{LOG} {file_name} already exists in {destination_folder}"))

                # Asking frontend for input
                print(f"{CHOICE} Overwrite or Skip?")

                # Checking if command yes or no
                user_input = input(":>> ")
                
                if user_input.lower() == 'overwrite':
                    # Deleting file in write destination
                    os.remove(join_paths(destination_folder, type_folder, file_name))
                    print(f"{LOG} Deleted original file")

                    # Keeping file the same, allowing later method to overwrite
                    print(f"{LOG} {file_name} moved to {destination_folder}")
                    break
                
                elif user_input.lower() == 'rename':
                    '''
                    while(True):
                        print("Rename file:")
                        new_name = input(":>> ")
                       
                        # Renaming file
                        if not os.path.exists(get_renamed_path(file_path,new_name)): 
                            file = rename_file(file_path,new_name), file[1]
                            break
                        else:
                            print("Name already taken")
                        # Instead of breaking, we loop back to beginning of while loop'''
                    
                elif user_input.lower() == 'skip':
                    # deleting all instances of 
                    files_to_move = [item for item in files_to_move if item != file]
                    print("Cancelled file move")
                    break
                else:
                    print(f"{ERROR} Invalid user input")
            else:
                break

    # If OK, extract
    move_files_to_destination(files_to_move,destination_folder)

    print("Done!")

if __name__ == "__main__":
    main()
