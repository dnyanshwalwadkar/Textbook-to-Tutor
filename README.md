# 📚 Project Ancient Aurora: Local AI for Native Education

**Build your own custom AI Tutor, fine-tuned on specific academic syllabi, running 100% locally on your device.**

---

## 🚀 The Mission
This project demonstrates how to **democratize AI for education**. We solve three massive problems in EdTech:
1.  **Language Barrier**: Most powerful LLMs are English-centric. We fine-tune them to be fluent in **Marathi** (or any native language).
2.  **Syllabus Relevance**: General models hallucinate. We force the model to learn *only* from the State Board Textbooks.
3.  **Cost & Privacy**: We run the final model **locally** on your laptop. No expensive cloud subscriptions, no data privacy issues.

## 🛠️ The "No-Cost" Tech Stack
We have carefully selected a stack that creates a state-of-the-art pipeline for **$0**.

| Component | Role | Why we chose it? |
| :--- | :--- | :--- |
| **Gemini 1.5 Pro** | **The Teacher** | Its massive context window (2M tokens) and superior OCR capabilities allow it to "read" complex PDF textbooks (tables, diagrams) better than any other model. We use the **Free Tier**. |
| **Llama 3 (8B)** | **The Student** | The best "small" open-source model. It is smart enough to learn complex topics but small enough to run on a standard laptop. |
| **Unsloth** | **The Accelerator** | A library that optimizes training. It makes fine-tuning **2x faster** and uses **60% less memory**, allowing us to train Llama 3 on a free Google Colab GPU (Tesla T4). |
| **Ollama** | **The Runtime** | The easiest way to run LLMs locally. It handles the complexity of GPU/CPU offloading on Mac and Windows. |

---

## ⚡ Workflow

### Step 1: Digitize (The Eyes) -> `step1_digitize_book.py`
We don't just extract text. We use **Gemini 1.5 Pro** to visually analyze every page.
*Result: A highly structured JSON representation of your textbook.*

> **🔒 Privacy Option (100% Local)**:
> If you don't want to send PDFs to Google, use **Ollama Vision** instead.
> 1. Run `ollama pull llama3.2-vision`
> 2. Run `python3 step1_digitize_book_local.py`
> *Note: This is slower and less accurate than Gemini, but runs offline.*

### Step 2: Synthesize (The Brain) -> `step2_generate_finetuning_data.py`
Raw text isn't enough. We need to teach the model *how to think*.
-   We ask Gemini to act as a "Curriculum Designer".
-   It generates **5-8 Q&A pairs per page**.
-   It creates **Reasoning Questions** ("Why did X happen?"), **Visual Analysis** questions, and **Factual** definitions.
*Result: A rich dataset (`.jsonl`) of thousands of high-quality examples.*

### Step 3: Train (The Muscle) -> `step3_train_llama.ipynb`
We take our synthetic data to **Google Colab**.
-   Using **Unsloth**, we fine-tune Llama 3 8B.
-   We use **LoRA (Low-Rank Adaptation)** to train only a small fraction of weights (efficient).
-   We export the result as a **GGUF** file (Quantized format for laptops).

### Step 4: Run (The Voice) -> Local Inference
We use **Ollama** to serve the model.
-   You chat with your custom model instantly.
-   It runs offline, private, and fast.

---

## 🏃‍♂️ Quick Start

### Prerequisites
1.  **Google API Key**: Get one for [free here](https://aistudio.google.com/).
2.  **Python 3.10+** & **Ollama** installed.

### Installation
```bash
git clone https://github.com/yourusername/ancient-aurora.git
cd ancient-aurora
pip install -r requirements.txt
```

### Configuration
Create a `.env` file:
```env
GOOGLE_API_KEY=your_api_key_here
```

### Usage
**1. Digitize your Book:**
Put your PDF in `raw_pdfs/` and run:
```bash
python3 step1_digitize_book.py
```

**2. Generate Training Data:**
```bash
python3 step2_generate_finetuning_data.py
```

**3. Train the Model:**
Upload `step3_train_llama.ipynb` and the generated `.jsonl` file to [Google Colab](https://colab.research.google.com/). Run all cells. Download the `.gguf` file.

**4. Run Locally:**
Move the `.gguf` file to this folder and run:
```bash
ollama create marathi-tutor -f Modelfile
ollama run marathi-tutor
```
