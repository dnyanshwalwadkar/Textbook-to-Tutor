# Marathi PDF to Llama 3 (Local)

This workspace detects and extracts content from Marathi text books, generates a training dataset, and fine-tunes Llama 3 to run locally on your Mac.

## Workflow

### Step 1: Digitize (Gemini API)
1.  **Add PDFs**: Put your Marathi PDF files in `raw_pdfs/`.
2.  **Run**: `python3 main.py`
3.  **Output**: `processed_dataset/*.json`

### Step 2: Teacher Script (Gemini API)
1.  **Run**: `python3 step2_generate_finetuning_data.py`
2.  **Output**: `finetuning_ready/*_finetune.jsonl`

### Step 3: Train (Google Colab)
1.  Open [Google Colab](https://colab.research.google.com/).
2.  Upload `step3_train_llama.ipynb` (from this folder).
3.  Upload your `.jsonl` file from Step 2.
4.  Run the notebook.
5.  **Download**: The resulting `unsloth.Q4_K_M.gguf` file.

### Step 4: Run Locally (Ollama)
1.  Install [Ollama](https://ollama.com/) on your Mac.
2.  Move the downloaded `.gguf` file to this folder.
3.  Create the model:
    ```bash
    ollama create marathi-history -f Modelfile
    ```
4.  Run it:
    ```bash
    ollama run marathi-history
    ```

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

3. **API Key (Secure)**:
   Create a file named `.env` in the project root and add your key:
   ```env
   GOOGLE_API_KEY=your_actual_api_key_here
   ```
   *Note: This file is ignored by git so your key stays private.*

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

