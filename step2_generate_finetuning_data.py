import google.generativeai as genai
import json
import os
import time
import typing_extensions
from pathlib import Path

# --- Configuration ---

INPUT_JSON_DIR = Path("./processed_dataset")
OUTPUT_DATA_DIR = Path("./finetuning_ready")
OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)

from dotenv import load_dotenv

# --- Configuration ---
load_dotenv() # Load variables from .env file

# We use Pro because Flash sometimes struggles with complex Marathi handwritten-style fonts 
# or dense academic layouts. Pro is slower but "High Standard."
MODEL_NAME = "gemini-2.5-flash" 

if "GOOGLE_API_KEY" not in os.environ:
    print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
    print("   Please create a .env file with GOOGLE_API_KEY='your_key'")
    exit(1)

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# --- Schema for Synthetic Data ---
# We force Gemini to output this specific list of Q&A pairs
class QA_Pair(typing_extensions.TypedDict):
    question: str
    answer: str
    type: str  # "reasoning", "visual_qa", or "factual"

class SyntheticPageData(typing_extensions.TypedDict):
    qa_pairs: list[QA_Pair]
    summary: str

# --- The "Teacher" Prompt ---
# This prompts the model to act as a curriculum designer
SYNTHESIS_PROMPT = """
You are an expert curriculum developer for Marathi State Board schools (Class 10).
I will provide you with the structured content of a single textbook page (JSON format).

Your task is to generate a **Fine-Tuning Dataset** from this content.

**Input Data Analysis:**
1. Read the `content_blocks`.
2. Pay special attention to blocks where `block_type` is "diagram" or "table".
3. Use the extracted `text` as the ground truth.

**Generation Requirements (Output in Marathi):**
Generate a JSON object containing:
1. **"summary"**: A concise paragraph explaining the core concept of this page.
2. **"qa_pairs"**: A list of 3-5 Question-Answer pairs:
   - **Visual QA**: If there is a diagram description, ask a question that requires understanding that visual (e.g., "Based on the map...").
   - **Reasoning**: Ask a "Why" or "How" question (Chain of Thought).
   - **Factual**: A direct concept definition.

**Tone:** Academic, helpful, and strictly in **Marathi**.
"""

def generate_instructions_from_book(json_path: Path):
    print(f"\n🧠 Synthesizing Training Data for: {json_path.name}")
    
    # Load the Step 1 Output
    with open(json_path, 'r', encoding='utf-8') as f:
        book_data = json.load(f)

    model = genai.GenerativeModel(MODEL_NAME)
    
    # We will save to a JSONL file (standard for LLM training)
    output_filename = OUTPUT_DATA_DIR / f"{json_path.stem}_finetune.jsonl"
    
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        
        total_pages = len(book_data.get("pages", []))
        
        for i, page in enumerate(book_data.get("pages", [])):
            page_num = page.get("page_number", i+1)
            print(f"   Processing Page {page_num}/{total_pages}...")

            # Construct the context string from Step 1 data
            # We flatten the JSON back into a readable string for the model to analyze
            page_context = f"Page {page_num} Content:\n"
            for block in page.get("content_blocks", []):
                b_type = block.get('block_type', 'text')
                content = block.get('content', '')
                desc = block.get('description', '')
                
                if b_type == "diagram":
                    page_context += f"[VISUAL: {desc}]\n"
                elif b_type == "table":
                    page_context += f"[TABLE: {content}]\n"
                else:
                    page_context += f"{content}\n"

            try:
                # Call Gemini to generate the Q&A pairs
                response = model.generate_content(
                    [SYNTHESIS_PROMPT, page_context],
                    generation_config={
                        "response_mime_type": "application/json",
                        "response_schema": SyntheticPageData
                    }
                )

                synthetic_data = json.loads(response.text)
                
                # --- FORMATTING FOR FINE-TUNING ---
                # We convert this into "ShareGPT" or "Alpaca" style format
                # Format: {"messages": [{"role": "user", "content": Q}, {"role": "assistant", "content": A}]}
                
                # 1. Add the Summary as a "text completion" training row
                summary_row = {
                    "messages": [
                        {"role": "user", "content": f"Summarize the concepts on page {page_num} of {book_data.get('book_name')}."},
                        {"role": "assistant", "content": synthetic_data['summary']}
                    ]
                }
                outfile.write(json.dumps(summary_row, ensure_ascii=False) + "\n")

                # 2. Add the Q&A Pairs
                for qa in synthetic_data.get('qa_pairs', []):
                    qa_row = {
                        "messages": [
                            {"role": "user", "content": qa['question']},
                            {"role": "assistant", "content": qa['answer']}
                        ],
                        "metadata": {
                            "type": qa['type'],
                            "source": f"{book_data.get('book_name')} - Page {page_num}"
                        }
                    }
                    outfile.write(json.dumps(qa_row, ensure_ascii=False) + "\n")

                # Rate limit handling
                time.sleep(1)

            except Exception as e:
                print(f"   ⚠️ Error generating data for Page {page_num}: {e}")
                continue

    print(f"✅ Training data saved to: {output_filename}")

def main():
    json_files = list(INPUT_JSON_DIR.glob("*_dataset.json"))
    
    if not json_files:
        print(f"⚠️ No processed JSON datasets found in {INPUT_JSON_DIR}. Run Step 1 first!")
        return

    for json_file in json_files:
        generate_instructions_from_book(json_file)

if __name__ == "__main__":
    main()