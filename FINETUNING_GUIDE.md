# 🧠 Deep Dive: Fine-Tuning & Technical Concepts

This document explains the **"Why"** and **"How"** of the engineering choices in Project Ancient Aurora. It serves as a technical manual for understanding what is happening under the hood when you train your model.

---

## 1. The Core Concept: SFT (Supervised Fine-Tuning)
We are using a technique called **SFT**.
*   **Pre-training**: The model (Llama 3) has read the entire internet. It knows English, general logic, and coding.
*   **Fine-tuning**: We show it specific examples (QA pairs) to teach it a *new behavior* or *specific knowledge domain* (Marathi History).
*   **Supervised**: We provide the "Correct Answer". It's like a teacher correcting a student's homework.

---

## 2. The Techniques (How we make it cheap)

### LoRA (Low-Rank Adaptation)
Training a 8 Billion parameter model normally requires massive supercomputers. We use **LoRA** to cheat.
*   **Idea**: Instead of changing *all* 8B weights, we freeze the main model and only train tiny "adapter" layers on top of it.
*   **The "Rank" (r=16)**:
    *   This determines how "smart" the adapter is.
    *   **Higher Rank (e.g., 64/128)**: Can learn more complex nuances but uses more memory.
    *   **Our Choice (r=16)**: A sweet spot for learning text styles without crashing the free Colab GPU.
*   **LoRA Alpha**: Scales the weight of the adapter. usually set to equal `r` or `2*r`.

### Quantization (4-bit)
*   **Float32 (Standard)**: Each number in the brain takes 32 bits of memory.
*   **4-bit (Our Choice)**: We compress each number to just 4 bits.
*   **Effect**: The model shrinks from ~16GB to ~5GB, allowing it to fit on a laptop or free cloud GPU.
*   **QLoRA**: Combining Quantization + LoRA. This is the industry standard for low-cost training.

---

## 3. The Engine: Unsloth
You will see `unsloth` in the training script.
*   **What is it?**: A rewritten version of the training mathematics manually optimized for NVIDIA GPUs.
*   **Why we chose it?**:
    *   **2x Faster**: Manual backprop kernels.
    *   **Less VRAM**: Smart memory management.
    *   **Accuracy**: Mathematical equivalent to standard HuggingFace (no quality loss).

---

## 4. Hyperparameters (The Knobs you can turn)

These are the settings in `step3_train_llama.ipynb`.

| Parameter | Value | What it does | Effect of changing |
| :--- | :--- | :--- | :--- |
| **Learning Rate** | `2e-4` | How fast the model learns. | **Too High**: It forgets English/Logic. **Too Low**: It learns nothing. |
| **Max Steps** | `60` | How many batches of data it sees. | **Increase to 100-300** for better results. If too high, it "overfits" (memorizes instead of learning). |
| **Batch Size** | `2` | How many examples it studies at once. | **Higher**: Faster, stable learning. **Lower**: Uses less memory. |
| **Gradient Accumulation** | `4` | Fakes a larger batch size. | Effectively `Batch * Accumulation = 8`. Allows "big batch" stability on small RAM. |
| **Temperature** | `0.3` | Creativity setting (In Modelfile). | **0.0**: Robotic/Precise. **1.0**: Creative/Random. We use 0.3 for factual accuracy. |

---

## 5. The Output: GGUF
We export to **GGUF** (GPT-Generated Unified Format).
*   This is a binary file format optimized for **CPU inference**.
*   It allows the model to run on your Mac (via `llama.cpp` under Ollama) using Apple's Metal Performance Shaders (MPS) instead of needing a dedicated NVIDIA card.
