import autoZip
from autoSort import move_files_to_destination, compile_files, compile_files_dir, type_files
from autoZip import extract_and_delete_zip_files, compile_zip_files
import tkinter as tk

from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog

import queue as q
import threading as th

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

def selectWindow(prompt_text, items):
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
 
class FileMoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Mover")

        # Variables for entry widgets
        self.source_folder_var = tk.StringVar()
        self.destination_folder_var = tk.StringVar()

        # Set up GUI elements
        self.setup_gui()

    def setup_gui(self):
        # Source Folder Entry
        tk.Label(self.root, text="Source Folder:").grid(row=0, column=0, sticky='e')
        tk.Entry(self.root, textvariable=self.source_folder_var, width=40).grid(row=0, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_source_folder).grid(row=0, column=2)

        # Destination Folder Entry
        tk.Label(self.root, text="Destination Folder:").grid(row=1, column=0, sticky='e')
        tk.Entry(self.root, textvariable=self.destination_folder_var, width=40).grid(row=1, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_destination_folder).grid(row=1, column=2)

        # Move Files Button
        tk.Button(self.root, text="Move Files", command=self.move_files).grid(row=2, column=1)

        # Output Text
        self.output_text = tk.Text(self.root, height=10, width=60)
        self.output_text.grid(row=3, column=0, columnspan=3)

    def browse_source_folder(self):
        folder_path = filedialog.askdirectory()
        self.source_folder_var.set(folder_path)

    def browse_destination_folder(self):
        folder_path = filedialog.askdirectory()
        self.destination_folder_var.set(folder_path)

    def move_files(self):
        source_folder = self.source_folder_var.get()
        destination_folder = self.destination_folder_var.get()

        zipYes = messagebox.askyesno("Unzip FIles?", f"Any files to unzip in {destination_folder}")

        # Making sure user approves of unzipping files
        if zipYes:

            files_to_zip = compile_zip_files(source_folder)
            files_to_zip = deleteWindow("Select which files to unzip:", files_to_zip)

            if len(files_to_zip) != 0:
                print(source_folder)
                print(destination_folder)
                extract_and_delete_zip_files(files_to_zip, source_folder, source_folder)
                messagebox.showinfo("Following files zipped:","\n".join(files_to_zip))
            else:
                print("Zip files cancelled") 
        else:
            pass

        # Call the existing script functionality
        files_to_move = compile_files_dir(source_folder)
        print(files_to_move)
        files_to_move = deleteWindow("Deselect any files you don't wish to move",files_to_move)

        print(files_to_move)

        files_with_types = type_files(files_to_move)

        # Check each filepair to see if the file has more than one possible type
        for filepair in files_with_types:
            if len(filepair[1]) <= 1:
                pass
            # Ask user to select which type this file is
            else:
                filepair[1] = [filepair[1][selectWindow(f"Select which type for {filepair[0]}", filepair[1])]]

                print("found multiple types")

        joined_files = convert_tuplelist_string(files_with_types)

        print(files_with_types)

        # If we are aproved to get the files
        if len(files_with_types) > 0:
             move_files_to_destination(files_with_types, destination_folder)
             messagebox.showinfo(f"Following files have been sorted to {destination_folder}:", joined_files)
        else:
            print("move files cancelled")
        
        # Update the output text
        self.output_text.delete(1.0, tk.END)  # Clear previous text
        self.output_text.insert(tk.END, "Files moved:\n")
        for file_info in files_to_move:
            self.output_text.insert(tk.END, f"{file_info[0]} - {file_info[1]}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileMoverApp(root)
    root.mainloop()
