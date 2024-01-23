import os
from PIL import Image
from fpdf import FPDF

# Define the path to the input and output directories
input_dir = 'input'
output_dir = 'output'

# Check if output directory exists, if not, create it
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Get a list of all the folders in the input directory
folders = os.listdir(input_dir)

# For each folder in the list
for folder in folders:
    print(f"Stitching {folder}...")
    # Get a list of all the images in the folder
    images = os.listdir(os.path.join(input_dir, folder))
    # Sort the list of images to ensure they are in the correct order
    images.sort()

    # Create a new PDF object
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=0)

    # For each image in the list
    for image in images:
        # Open the image and get its size
        img = Image.open(os.path.join(input_dir, folder, image))
        width, height = img.size
        # Convert the image size from pixels to points
        width_pt = width * 0.264583
        height_pt = height * 0.264583
        # Add a page to the PDF with the image size
        pdf.add_page(format=(width_pt, height_pt))
        pdf.image(os.path.join(input_dir, folder, image), 0, 0, width_pt, height_pt)
    # Save the PDF file with the same name as the folder in the output directory
    pdf.output(os.path.join(output_dir, f"{folder}.pdf"))
    print(f"Stitched {folder}! Folders left: {len(folders) - folders.index(folder) - 1}")