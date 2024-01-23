from PyPDF2 import PdfFileReader
from pdf2image import convert_from_path
from PIL import Image

path = "path"


def extract_images(pdf_path, coords1, coords2):
    pdf = PdfFileReader(pdf_path)
    num_pages = pdf.getNumPages()
    for i in range(num_pages):
        images = convert_from_path(pdf_path, first_page=i + 1, last_page=i + 1)
        for j, image in enumerate(images):
            # Crop image for the first rectangle and save
            cropped_image1 = image.crop(coords1)
            cropped_image1.save(f"output_{i * 2 + j + 1}.png")
            print(i)
            # Crop image for the second rectangle and save
            cropped_image2 = image.crop(coords2)
            cropped_image2.save(f"output_{i * 2 + j + 2}.png")


# Example usage
extract_images(path, (300, 323, 1369, 1055), (300, 1283, 1369, 2015))


def extract_test_image(pdf_path):
    pdf = PdfFileReader(pdf_path)
    num_pages = pdf.getNumPages()

    for i in range(num_pages):
        images = convert_from_path(pdf_path, first_page=i + 1, last_page=i + 1)
        for j, image in enumerate(images):
            while True:
                coords1 = tuple(
                    map(int, input("Enter coordinates for the first rectangle (x1, y1, x2, y2): ").split(',')))

                # Crop image for the first rectangle and save
                cropped_image1 = image.crop(coords1)
                cropped_image1.save(f"test_output_{i * 2 + j + 1}.png")

                if input("Are you satisfied with the result? (yes/no): ").lower() == 'yes':
                    break

# extract_test_image("/home/intron014/UPM/CITIT21-AL/PDF Extractor/a.pdf")
