import autoZip
from autoSort import move_files_to_destination, compile_files
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

def convert_tuplelist_string(data: List[Tuple[str, List]]) -> str:
    result = "["
    for item in data:
        result += f"('{item[0]}', {item[1]}), "
    result = result.rstrip(", ") + "]"
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
            zipAprove = messagebox.askokcancel("Unzip the following files?", '.\n'.join(files_to_zip))

            if zipAprove:
                print(source_folder)
                print(destination_folder)
                extract_and_delete_zip_files(files_to_zip, source_folder, source_folder)
                messagebox.showinfo("Following files zipped:","\n".join(files_to_zip))
            else:
                pass
        else:
            pass

        # Call the existing script functionality
        files_to_move = compile_files(source_folder)
        joined_files = convert_tuplelist_string(files_to_move)

        move_yes = messagebox.askokcancel(f"Sort following files to {destination_folder}?", joined_files)

        # If we are aproved to get the files
        if move_yes:
             move_files_to_destination(files_to_move, destination_folder)
             messagebox.showinfo(f"Following files have been sorted to {destination_folder}:", joined_files)

        # Update the output text
        self.output_text.delete(1.0, tk.END)  # Clear previous text
        self.output_text.insert(tk.END, "Files moved:\n")
        for file_info in files_to_move:
            self.output_text.insert(tk.END, f"{file_info[0]} - {file_info[1]}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileMoverApp(root)
    root.mainloop()
