import os
from pypdf import PdfReader
from .text_chunker import chunk_pdf_metadata

def extract_pdf_content(pdf_path, output_dir='dist'):
    reader = PdfReader(pdf_path)
    pages = reader.pages
    
    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
    
    page_content = []
    for page_num, page in enumerate(pages):
        images = page.images
        text_extract = page.extract_text()

        extracted_images = []
        for i, image_file_object in enumerate(images):
            file_name = f"out-image-{page_num}-{i}-{image_file_object.name}"
            file_path = os.path.join(output_dir, 'images', file_name)
            image_file_object.image.save(file_path)
            extracted_images.append(file_path)
        
        text_extract = text_extract.replace('-\n', '').replace('\n', ' ')
        text_extract = ' '.join(text_extract.split())
        
        page_content.append({
            'page': page_num + 1,
            'text': text_extract,
            'images': extracted_images
        })
    
    return page_content, reader.metadata.title or os.path.basename(pdf_path)

def process_pdf(pdf_path, chunk_size=1000, overlap=200, output_dir='dist'):
    page_content, title = extract_pdf_content(pdf_path, output_dir)
    return chunk_pdf_metadata(page_content, title, chunk_size, overlap)
