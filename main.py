import google.generativeai as genai
import os
import json
import time
import typing_extensions
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image

# --- Configuration ---
# We use Pro because Flash sometimes struggles with complex Marathi handwritten-style fonts 
# or dense academic layouts. Pro is slower but "High Standard."
MODEL_NAME = "gemini-2.5-flash" 

if "GOOGLE_API_KEY" not in os.environ:
    # Replace with your actual key
    os.environ["GOOGLE_API_KEY"] = "AIzaSyAtzSq0M-vbTKowuRJBeMqyb2DDyzpSQPs"

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# --- Directories ---
INPUT_PDF_DIR = Path("/Users/dnyaneshwalwadkar/Documents/DATA/MarathiBooks/")  # Put your Marathi PDFs here
OUTPUT_JSON_DIR = Path("./processed_dataset")
OUTPUT_JSON_DIR.mkdir(parents=True, exist_ok=True)

# --- Define the JSON Schema for the Model ---
# This enforces the "Smart Dataset" structure we discussed.
class ContentBlock(typing_extensions.TypedDict):
    block_type: str  # e.g., "text", "diagram", "table", "sidebar"
    content: str     # The actual Marathi text or Table Markdown
    description: str # (For Images only) Detailed visual description
    concept_tags: list[str] # Concepts detected in this block

class PageAnalysis(typing_extensions.TypedDict):
    page_number: int
    content_blocks: list[ContentBlock]
    page_summary: str
    links_to_previous: str # How this page connects to concepts previously mentioned

# --- System Prompt ---
SYSTEM_PROMPT = """
You are an expert AI creating a high-quality dataset for Fine-Tuning LLMs on Marathi State Board Textbooks.
Your goal is to digitize this textbook page image into a structured format.

**CRITICAL INSTRUCTIONS:**
1. **OCR (Text Extraction):** Transcribe all Marathi text exactly as it appears (Devanagari script). Do not translate.
2. **Visual Analysis:** - If you see a **Diagram, Map, or Graph**: Set `block_type` to "diagram". In the `description` field, write a highly detailed caption describing the visual elements (e.g., "A pie chart showing land usage, 40% agriculture..."). This is crucial for the LLM to "learn" the image.
   - If you see a **Table**: Set `block_type` to "table". Convert the table into Markdown format in the `content` field.
3. **Sidebar Detection:** If there is a "Do You Know?" (माहीत आहे का तुम्हाला?) box, mark it as `block_type`: "sidebar".
4. **Context Linking:** Briefly explain in `links_to_previous` if this page continues a sentence or concept from a typical previous page flow.

**OUTPUT:** Return ONLY valid JSON adhering to the requested schema.
"""

def process_pdf_syllabus(pdf_path: Path):
    print(f"\n📘 Processing Book: {pdf_path.name}")
    
    # 1. Convert PDF to Images
    print("   Converting PDF to images...")
    try:
        # 300 DPI is standard for high-quality OCR
        pages = convert_from_path(str(pdf_path), dpi=300)
    except Exception as e:
        print(f"   ❌ Error converting PDF: {e}")
        print("      (Make sure Poppler is installed and in your PATH)")
        return

    book_data = {
        "book_name": pdf_path.stem,
        "total_pages": len(pages),
        "pages": []
    }

    model = genai.GenerativeModel(MODEL_NAME)

    # 2. Iterate through pages
    for i, page_image in enumerate(pages):
        page_num = i + 1
        print(f"   Processing Page {page_num}/{len(pages)}...")

        try:
            # We use `generation_config` to enforce JSON output (Gemini feature)
            response = model.generate_content(
                [SYSTEM_PROMPT, page_image],
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": PageAnalysis
                }
            )
            
            # Parse the JSON response
            page_json = json.loads(response.text)
            
            # Add metadata to the page object
            page_json["page_number"] = page_num
            book_data["pages"].append(page_json)
            
            # Rate limit handling (Safety pause)
            time.sleep(2) 

        except Exception as e:
            print(f"   ⚠️ Error on Page {page_num}: {e}")
            # Continue to next page even if one fails
            continue

    # 3. Save the Book Dataset
    output_file = OUTPUT_JSON_DIR / f"{pdf_path.stem}_dataset.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(book_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Finished! Saved dataset to: {output_file}")

def main():
    print(f"📂 Scanning for PDFs in: {INPUT_PDF_DIR}")
    
    # Create input dir if not exists
    INPUT_PDF_DIR.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(INPUT_PDF_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️ No PDFs found in {INPUT_PDF_DIR}. Please add some Marathi textbook PDFs.")
        return

    for pdf in pdf_files:
        process_pdf_syllabus(pdf)

if __name__ == "__main__":
    main()
