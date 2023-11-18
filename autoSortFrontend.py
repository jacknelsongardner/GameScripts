import autoZip
from autoSort import move_files_to_destination, compile_files

import tkinter as tk
from tkinter import filedialog

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

        # Call the existing script functionality
        files_to_move = compile_files(source_folder)
        move_files_to_destination(files_to_move, destination_folder)

        # Update the output text
        self.output_text.delete(1.0, tk.END)  # Clear previous text
        self.output_text.insert(tk.END, "Files moved:\n")
        for file_info in files_to_move:
            self.output_text.insert(tk.END, f"{file_info[0]} - {file_info[1]}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileMoverApp(root)
    root.mainloop()
