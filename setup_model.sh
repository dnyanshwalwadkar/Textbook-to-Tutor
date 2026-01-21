#!/bin/bash

# Configuration
MODEL_NAME="marathi-10th-history-civics"
GGUF_FILE="unsloth.Q4_K_M.gguf"
MODELFILE="Modelfile"

echo "🤖 Setting up your local AI Tutor: $MODEL_NAME"

# 1. Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Error: Ollama is not installed."
    echo "   Please install it from https://ollama.com/"
    exit 1
fi

# 2. Check if the GGUF file exists
if [ ! -f "$GGUF_FILE" ]; then
    echo "❌ Error: Could not find '$GGUF_FILE' in this folder."
    echo "   Please move the downloaded file from your Downloads folder to here:"
    echo "   $(pwd)"
    exit 1
fi

# 3. Create the model
echo "📦 Creating Ollama model..."
ollama create $MODEL_NAME -f $MODELFILE

# 4. Success message
if [ $? -eq 0 ]; then
    echo "✅ Success! Model '$MODEL_NAME' created."
    echo ""
    echo "   To chat with it, run:"
    echo "   ollama run $MODEL_NAME"
    echo ""
    read -p "   Do you want to run it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ollama run $MODEL_NAME
    fi
else
    echo "❌ Error creating model."
fi
