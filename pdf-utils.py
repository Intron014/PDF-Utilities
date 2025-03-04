import os
import argparse
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import img2pdf
import glob

def extract_slides_from_pdf(pdf_path, output_dir):
    """
    Extract slides from a PDF by splitting each page horizontally and detecting squares in each half.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Base output directory
    """
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    pdf_output_dir = os.path.join(output_dir, pdf_name)
    os.makedirs(pdf_output_dir, exist_ok=True)
    images = convert_from_path(pdf_path)
    slide_count = 0

    for i, page_image in enumerate(images):
        width, height = page_image.size
        top_half = page_image.crop((0, 0, width, height // 2))
        bottom_half = page_image.crop((0, height // 2, width, height))
        top_slides = find_slides_in_image(top_half)
        bottom_slides = find_slides_in_image(bottom_half)
        
        if not top_slides and not bottom_slides:
            continue
            
        for slide in top_slides + bottom_slides:
            slide_count += 1
            slide.save(os.path.join(pdf_output_dir, f"{slide_count:03d}.png"))
        
        print(f"Processed page {i+1} from {pdf_name}, found {len(top_slides)} slides in top half and {len(bottom_slides)} slides in bottom half")
    
    if slide_count > 0:
        create_pdf_from_images(pdf_output_dir, os.path.join(pdf_output_dir, f"{pdf_name}_slides.pdf"))
    
    return slide_count

def find_slides_in_image(pil_image):
    """
    Try to detect slides (rectangles) in the image.
    Returns a list of PIL Image objects representing the slides.
    """
    img_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    slides = []
    if contours:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        contour = contours[0]
        x, y, w, h = cv2.boundingRect(contour)
        img_area = img_cv.shape[0] * img_cv.shape[1]
        contour_area = w * h
        
        if contour_area > 0.1 * img_area:
            slide = pil_image.crop((x, y, x+w, y+h))
            slides.append(slide)
    
    return slides

def create_pdf_from_images(images_dir, output_pdf_path):
    """
    Create a PDF with one image per page from all PNG images in the specified directory.
    
    Args:
        images_dir: Directory containing images
        output_pdf_path: Path where the output PDF will be saved
    """
    image_files = sorted(glob.glob(os.path.join(images_dir, "*.png")), 
                        key=lambda x: int(os.path.basename(x).split('.')[0]))
    
    if not image_files:
        print(f"No images found in {images_dir} to create PDF")
        return False
    
    with open(output_pdf_path, "wb") as f:
        f.write(img2pdf.convert(image_files))
    
    print(f"Created PDF with {len(image_files)} pages at {output_pdf_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Extract slides from PDFs by splitting pages horizontally")
    parser.add_argument("--input", "-i", default="input", help="Input directory containing PDFs")
    parser.add_argument("--output", "-o", default="out", help="Output directory for extracted slides")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        os.makedirs(args.input)
        print(f"Created input directory: {args.input}")
        
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        print(f"Created output directory: {args.output}")
    
    pdf_count = 0
    total_slides = 0
    for filename in os.listdir(args.input):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(args.input, filename)
            print(f"Processing PDF: {filename}")
            slides = extract_slides_from_pdf(pdf_path, args.output)
            total_slides += slides
            pdf_count += 1
    
    if pdf_count == 0:
        print(f"No PDF files found in {args.input}")
    else:
        print(f"Processed {pdf_count} PDF files. Extracted {total_slides} slides to {args.output}")

if __name__ == "__main__":
    main()