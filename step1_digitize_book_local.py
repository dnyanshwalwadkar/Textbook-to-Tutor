import ollama
import os
import json
import time
import io
import typing_extensions
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image

# --- Configuration ---
# You must pull this model first: `ollama pull llama3.2-vision`
MODEL_NAME = "llama3.2-vision" 

# --- Directories ---
INPUT_PDF_DIR = Path("./raw_pdfs")
OUTPUT_JSON_DIR = Path("./processed_dataset")
OUTPUT_JSON_DIR.mkdir(parents=True, exist_ok=True)

# --- System Prompt ---
# Llama 3.2 Vision is smaller, so we use a simpler, more direct prompt.
SYSTEM_PROMPT = """
You are aocr assistant. Analyze this image of a text book page.
Return a VALID JSON object with this exact structure:
{
  "content_blocks": [
    {
       "block_type": "text", 
       "content": "extracted text here" 
    },
    {
       "block_type": "diagram",
       "description": "visual description of the diagram"
    }
  ],
  "page_summary": "brief summary"
}

Rules:
1. Extract ALL text in Marathi.
2. If you see a diagram/image, describe it.
3. OUTPUT ONLY JSON.
"""

def process_pdf_local(pdf_path: Path):
    print(f"\n📘 (Local) Processing Book: {pdf_path.name}")
    
    print("   Converting PDF to images...")
    try:
        pages = convert_from_path(str(pdf_path), dpi=200) # Lower DPI for local speed
    except Exception as e:
        print(f"   ❌ Error converting PDF: {e}")
        return

    book_data = {
        "book_name": pdf_path.stem,
        "total_pages": len(pages),
        "pages": []
    }

    print(f"   Using Local Model: {MODEL_NAME}")
    
    for i, page_image in enumerate(pages):
        page_num = i + 1
        print(f"   Processing Page {page_num}/{len(pages)}...")

        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        page_image.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()

        try:
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[
                    {
                        'role': 'user',
                        'content': SYSTEM_PROMPT,
                        'images': [img_bytes]
                    }
                ],
                format='json', # Enforce JSON mode
                options={'temperature': 0}
            )
            
            # Parse JSON
            raw_text = response['message']['content']
            page_json = json.loads(raw_text)
            
            page_json["page_number"] = page_num
            book_data["pages"].append(page_json)

        except Exception as e:
            print(f"   ⚠️ Error on Page {page_num}: {e}")
            continue

    output_file = OUTPUT_JSON_DIR / f"{pdf_path.stem}_dataset.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(book_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Finished! Saved local dataset to: {output_file}")

def main():
    print(f"📂 Scanning for PDFs in: {INPUT_PDF_DIR}")
    INPUT_PDF_DIR.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(INPUT_PDF_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️ No PDFs found in {INPUT_PDF_DIR}.")
        return

    # Check if model exists
    try:
        ollama.show(MODEL_NAME)
    except:
        print(f"❌ Model '{MODEL_NAME}' not found. Please run: ollama pull {MODEL_NAME}")
        return

    for pdf in pdf_files:
        process_pdf_local(pdf)

if __name__ == "__main__":
    main()
