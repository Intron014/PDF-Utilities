import cv2
import numpy as np
from PyPDF2 import PdfFileReader
from pdf2image import convert_from_path
import os
import glob


def find_rectangles(image):
    open_cv_image = np.array(image)
    img_gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

    _, thresholded = cv2.threshold(img_gray, 240, 255, cv2.THRESH_BINARY_INV)

    height, width = img_gray.shape
    top_half = thresholded[0:height//2, :]
    bottom_half = thresholded[height//2:, :]

    contours_top, _ = cv2.findContours(top_half, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    standw = 1000
    standh = 700

    rectangles_top = []

    for contour in contours_top:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(contour)
            if w >= standw and h >= standh:
                rectangles_top.append((x, y, x+w, y+h))
                # print(f"Rectangle found in top half with size {w}x{h}")

    contours_bottom, _ = cv2.findContours(bottom_half, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    rectangles_bottom = []

    for contour in contours_bottom:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(contour)
            if w >= standw and h >= standh:
                rectangles_bottom.append((x, y + height//2, x+w, y+h + height//2))
                # print(f"Rectangle found in bottom half with size {w}x{h}")
    return rectangles_top + rectangles_bottom


def extract_images_v1(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    pdf = PdfFileReader(pdf_path)
    num_pages = pdf.getNumPages()
    pdfname = os.path.splitext(os.path.basename(pdf_path))[0]

    for i in range(num_pages):
        if i < 9:
            print(f"Looking for rectangles in page 0{i+1}, file: {pdfname}")
        else:
            print(f"Looking for rectangles in page {i+1}, file: {pdfname}")
        images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1)
        for j, image in enumerate(images):
            rectangles = find_rectangles(image)
            for k, coords in enumerate(rectangles):
                cropped_image = image.crop(coords)
                cropped_image.save(os.path.join(output_folder, f"{pdfname}_{i*len(rectangles)+k+1}.png"))
                # print(f"Saved rectangle {k+1} from page {i+1} as {pdfname}_{i*len(rectangles)+k+1}.png")


def extract_images_v2(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    pdf = PdfFileReader(pdf_path)
    num_pages = pdf.getNumPages()

    max_num = num_pages * 2
    num_digits = len(str(max_num))

    pdfname = os.path.splitext(os.path.basename(pdf_path))[0]

    total_rectangles = 0

    for i in range(num_pages):
        if i < 9:
            print(f"Looking for rectangles in page 0{i+1}, file: {pdfname}")
        else:
            print(f"Looking for rectangles in page {i+1}, file: {pdfname}")
        images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1)
        for j, image in enumerate(images):
            rectangles = find_rectangles(image)
            for k, coords in enumerate(rectangles):
                cropped_image = image.crop(coords)
                total_rectangles += 1
                output_file = f"{pdfname}_{total_rectangles:0{num_digits}d}.png"
                cropped_image.save(os.path.join(output_folder, output_file))
                # print(f"Saved rectangle {total_rectangles} from page {i+1} as {output_file}")


def bulk_extract_images(method):
    pdf_files = glob.glob("input/*.pdf")
    for pdf_file in pdf_files:
        output_folder = os.path.join("output", os.path.splitext(os.path.basename(pdf_file))[0])
        if method:
            extract_images_v1(pdf_file, output_folder)
        else:
            extract_images_v2(pdf_file, output_folder)


bulk_extract_images(0)
