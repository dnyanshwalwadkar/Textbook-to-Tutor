# Marathi PDF to Dataset Converter

This workspace detects and extracts content from Marathi text books using the Gemini 1.5 Pro API.

## Setup

1. **Install System Dependencies**:
   You need `poppler` for PDF processing.
   ```bash
   brew install poppler
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **API Key**:
   Set your Google Gemini API key:
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```
   Or edit `main.py` to include it directly (not recommended for sharing code).

## Usage

1. Place your Marathi PDF files in the `raw_pdfs` folder.
2. Run the script:
   ```bash
   python3 main.py
   ```
3. The processed JSON datasets will appear in `processed_dataset`.

## Output Format

The output is a JSON file for each book containing:
- `page_number`
- `block_type`: "text", "diagram", "table", "sidebar"
- `content`: Extracted text or markdown table
- `description`: For diagrams
- `concept_tags`: Detected concepts

