import os
from PIL import Image
import sys

from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import subprocess

coverart_dimensions = {
    "SLEEVE:PS2" : [273,184],
    "SLEEVE:GC" : [273,184]
}

def print_image(source_path, destination_path, pdf_name, print_width_mm, print_height_mm):
    try:
        # Open the image
        img = Image.open(source_path)

        print_width_inch = print_width_mm * 72 / 25.4
        print_height_inch = print_height_mm * 72 / 25.4

        # Create a PDF file with the desired dimensions
        pdf_path = os.path.join(destination_path,f"{pdf_name}.pdf")
        pdf = canvas.Canvas(pdf_path, pagesize=(print_width_inch, print_height_inch))
        pdf.drawInlineImage(source_path, 0, 0, width=print_width_inch, height=print_height_inch)
        pdf.save()

        print(f"Image '{source_path}' saved to {pdf_path}")

    except Exception as e:
        print(f"Error creating image: {e}")

def main():
    # Check if there are at least three command-line arguments (including the script name)
    if len(sys.argv) != 5:
        print("Usage: python script.py source_folder destination_folder pdf_name image_type")
        return
    
    # Access command-line arguments
    source_image = os.path.join(os.path.expanduser("~"), sys.argv[1])
    destination_folder = os.path.join(os.path.expanduser("~"), sys.argv[2])
    pdf_name = sys.argv[3]
    image_type = sys.argv[4]

    print(f"Source Folder: {source_image}")
    print(f"Destination Folder: {destination_folder}")

    print_image(source_image, destination_folder, pdf_name, coverart_dimensions[image_type][0], coverart_dimensions[image_type][1])

if __name__ == "__main__":
    main()

