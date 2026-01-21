# 🦙 Ollama Model Guide

This document explains how to take your fine-tuned GGUF file and turn it into a runnable local AI model using Ollama.

## prerequisites
-   **Ollama Installed**: [Download here](https://ollama.com/).
-   **GGUF File**: You must have `unsloth.Q4_K_M.gguf` (downloaded from Google Colab).

---

## 🚀 The Fast Way (Automated)

We have provided a script to do everything for you.
1.  Place `unsloth.Q4_K_M.gguf` in this folder.
2.  Run:
    ```bash
    ./setup_model.sh
    ```
This will create the model `marathi-10th-history-civics` and start a chat.

---

## 🛠️ The Manual Way (Step-by-Step)

If you want to understand what is happening, here are the commands.

### 1. The `Modelfile`
We use a file named `Modelfile` to configure the model. It looks like this:
```dockerfile
FROM ./unsloth.Q4_K_M.gguf
SYSTEM "You are an expert AI tutor specialized in Marathi State Board History..."
PARAMETER temperature 0.3
```
-   **FROM**: Points to the raw weights (GGUF).
-   **SYSTEM**: Sets the personality/behavior.
-   **PARAMETER**: Controls creativity (0.3 = focused/factual).

### 2. Create the Model
Run this command to "build" the model inside Ollama database:
```bash
ollama create marathi-10th-history-civics -f Modelfile
```
*Note: This might take a few seconds to import the weights.*

### 3. Run the Model
Start chatting with your custom AI:
```bash
ollama run marathi-10th-history-civics
```

---

## 🗑️ Managing Models

**List all models:**
```bash
ollama list
```

**Remove this model (to free space):**
```bash
ollama rm marathi-10th-history-civics
```
