import autoZip
from autoSort import *
from autoZip import extract_and_delete_zip_files, compile_zip_files
import tkinter as tk

from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk

import queue as q
import threading as th

import os

from typing import List, Tuple

logQ: q = q.Queue()
errorQ: q = q.Queue()

# converts list of tuples to string for user requests on the frontend
def convert_tuplelist_string(data: List[Tuple[str, List]]) -> str:
    result = "["
    for item in data:
        result += f"('{item[0]}', {item[1]}), "
    result = result.rstrip(", ") + "]"
    return result

# a window asking user to delete certain elements from text
def deleteWindow(prompt_text, my_list):
    def delete_item():
        selected_item = listbox.curselection()
        if selected_item:
            my_list.pop(selected_item[0])
            listbox.delete(selected_item[0])

    def ok_button():
        root.destroy()

    def cancel_button():
        while my_list:
            my_list.pop()
            listbox.delete(0)

        root.destroy()

    root = tk.Tk()
    root.title("Delete Items")

    label = tk.Label(root, text=prompt_text)
    label.pack(pady=10)

    listbox = tk.Listbox(root, selectmode=tk.SINGLE)
    for item in my_list:
        listbox.insert(tk.END, item)
    listbox.pack(pady=10)

    delete_button = tk.Button(root, text="Delete", command=delete_item)
    delete_button.pack(side=tk.LEFT, padx=5)

    ok_button = tk.Button(root, text="OK", command=ok_button)
    ok_button.pack(side=tk.RIGHT, padx=5)

    cancel_button = tk.Button(root, text="Cancel", command=cancel_button)
    cancel_button.pack(side=tk.RIGHT, padx=5)

    root.wait_window()  # Wait for the window to be destroyed before continuing

    return my_list

def selectIndexWindow(prompt_text, items):
    result = None

    def ok_button():
        nonlocal result
        selected_item = listbox.curselection()
        if selected_item:
            result = selected_item[0]
        root.destroy()

    def cancel_button():
        root.destroy()

    root = tk.Tk()
    root.title("Select Item")

    label = tk.Label(root, text=prompt_text)
    label.pack(pady=10)

    listbox = tk.Listbox(root, selectmode=tk.SINGLE)
    for item in items:
        listbox.insert(tk.END, item)
    listbox.pack(pady=10)

    ok_button = tk.Button(root, text="OK", command=ok_button)
    ok_button.pack(side=tk.RIGHT, padx=5)

    cancel_button = tk.Button(root, text="Cancel", command=cancel_button)
    cancel_button.pack(side=tk.RIGHT, padx=5)

    root.wait_window()

    return result
 
def selectWindow(prompt_text, items):
    result = None

    def ok_button():
        nonlocal result
        selected_item = listbox.curselection()
        if selected_item:
            result = items[selected_item[0]]
        root.destroy()

    def cancel_button():
        root.destroy()

    root = tk.Tk()
    root.title("Select Item")

    label = tk.Label(root, text=prompt_text)
    label.pack(pady=10)

    listbox = tk.Listbox(root, selectmode=tk.SINGLE)
    for item in items:
        listbox.insert(tk.END, item)
    listbox.pack(pady=10)

    ok_button = tk.Button(root, text="OK", command=ok_button)
    ok_button.pack(side=tk.RIGHT, padx=5)

    cancel_button = tk.Button(root, text="Cancel", command=cancel_button)
    cancel_button.pack(side=tk.RIGHT, padx=5)

    root.wait_window()

    return result

class FileMoverApp:
    def __init__(self, master):
        self.master = master
        self.master.title("File Mover App")
        self.master.geometry("800x600")

        # Create a PanedWindow for resizable divider
        self.paned_window = tk.PanedWindow(master, orient=tk.HORIZONTAL, sashrelief=tk.GROOVE, handlesize=10)
        self.paned_window.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Create a Frame for the left side
        left_frame = tk.Frame(self.paned_window)
        self.paned_window.add(left_frame)

        # Create Listbox for user clickable list
        self.file_listbox = tk.Listbox(left_frame, width=50, height=10, selectmode=tk.SINGLE)
        self.file_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a Frame for the right side
        right_frame = tk.Frame(self.paned_window)
        self.paned_window.add(right_frame)

        # Source Folder Entry
        self.source_folder_label = tk.Label(right_frame, text="Source Folder:")
        self.source_folder_label.pack(side=tk.TOP, pady=5)
        self.source_folder_entry = tk.Entry(right_frame)
        self.source_folder_entry.pack(side=tk.TOP, pady=5)
        self.browse_source_button = tk.Button(right_frame, text="Browse", command=self.browse_source)
        self.browse_source_button.pack(side=tk.TOP, pady=5)

        # Destination Folder Entry
        self.dest_folder_label = tk.Label(right_frame, text="Destination Folder:")
        self.dest_folder_label.pack(side=tk.TOP, pady=5)
        self.dest_folder_entry = tk.Entry(right_frame)
        self.dest_folder_entry.pack(side=tk.TOP, pady=5)
        self.browse_dest_button = tk.Button(right_frame, text="Browse", command=self.browse_dest)
        self.browse_dest_button.pack(side=tk.TOP, pady=5)

        # Move Files Button
        self.move_button = tk.Button(right_frame, text="Move Files", command=self.move_files)
        self.move_button.pack(side=tk.TOP, pady=5)

        # Log Textbox
        self.log_text = tk.Text(master, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(side=tk.BOTTOM, fill=tk.BOTH, pady=10)

    def browse_source(self):
        folder_path = filedialog.askdirectory()
        self.source_folder_entry.delete(0, tk.END)
        self.source_folder_entry.insert(0, folder_path)

    def browse_dest(self):
        folder_path = filedialog.askdirectory()
        self.dest_folder_entry.delete(0, tk.END)
        self.dest_folder_entry.insert(0, folder_path)

    def move_files(self):
        source_folder = self.source_folder_entry.get()
        destination_folder = self.dest_folder_entry.get()

        zipYes = messagebox.askyesno("Unzip FIles?", f"Any files to unzip in {destination_folder}")

        # Making sure user approves of unzipping files
        if zipYes:

            files_to_zip = compile_zip_files(source_folder)
            files_to_zip = deleteWindow("Select which files to unzip:", files_to_zip)

            if len(files_to_zip) != 0:
                messagebox.showinfo("Notice","Unzipping files may take some time. Please be patient.")

                extract_and_delete_zip_files(files_to_zip, source_folder, source_folder)

                messagebox.showinfo("Following files zipped:","\n".join(files_to_zip))
            else:
                messagebox.showinfo("Cancelled",f"File move was cancelled. Selected files will remain in the source folder.")
        else:
            pass

        # Call the existing script functionality
        files_to_move = compile_files_dir(source_folder)
        
        files_to_move = deleteWindow("Deselect any files you don't wish to move",files_to_move)

        files_with_types = type_files(files_to_move)
        
        # Check each filepair to see if the file has more than one possible type
        i = 0
        for filepair in files_with_types:
            if len(filepair[1]) <= 1:
                pass
            # Ask user to select which type this file is
            else:

                selected_item = selectWindow("Select an item to keep:", filepair[1])

                if selected_item is not None:
                    newfilepair = filepair[0], [selected_item]
                    files_with_types[i] = newfilepair
                else:
                    messagebox.showinfo("Cancelled",f"File move cancelled.")
            
            i = i + 1


        # Check each element to make sure they don't have elements that already exist
        for file in files_with_types:
        
            while(True):
                file_path = file[0]
                type_folder = type_to_folder[file[1][0]]
                file_name = get_entry_name(file[0])

                if path_exists(os.path.join(destination_folder, type_folder, file_name)):
                    overwriteOk = messagebox.askokcancel("f {file_name} already exists in {destination_folder}", "Overwrite file?")
                
                    if overwriteOk:
                        # Deleting file in write destination
                        os.remove(join_paths(destination_folder, type_folder, file_name))

                        messagebox.showinfo("Success!", f"Deleted original file, moved {file_name} to {destination_folder}")
                        break
                
                    else:
                        # deleting all instances of 
                        files_to_move = [item for item in files_to_move if item != file]
                        messagebox.showinfo("Cancelled overwrite")
                        break
                else:
                    break

        print(files_with_types)

        joined_files = convert_tuplelist_string(files_with_types)

        print(files_with_types)

        # If we are aproved to get the files
        if len(files_with_types) > 0:

            # Create pop up notifying user this may take a while
            popup = tk.Toplevel(root)
            popup.title("Popup Window")
            label = tk.Label(popup, text="Moving files ")
            label.pack(padx=20, pady=20)
             
            # Moving files to destination
            move_files_to_destination(files_with_types, destination_folder)
            messagebox.showinfo(f"Following files have been sorted to {destination_folder}:", joined_files)
        
            popup.destroy()
        else:
            messagebox.showinfo("Cancelled",f"File move was cancelled. Selected files will remain in the source folder.")
            
        # Update the output text
        self.output_text.delete(1.0, tk.END)  # Clear previous text
        self.output_text.insert(tk.END, "Files moved:\n")
        for file_info in files_to_move:
            self.output_text.insert(tk.END, f"{file_info[0]} - {file_info[1]}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileMoverApp(root)
    root.mainloop()
