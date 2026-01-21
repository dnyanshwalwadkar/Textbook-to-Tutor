import ollama
import sys
import time

# Configuration
MODEL_NAME = "marathi-10th-history-civics"

def type_writer(text):
    """Effect to print text like a typewriter"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.01)
    print()

def main():
    print(f"\n🎓 Initializing {MODEL_NAME}...\n")

    # 1. Check if model exists
    try:
        models = ollama.list()
        # ollama.list returns a dictionary object, we need to extract model names
        # Assuming different versions of the library, we handle robustly
        found = False
        for m in models.get('models', []):
            if MODEL_NAME in m.get('name', ''):
                found = True
                break
        
        if not found:
            print(f"❌ Model '{MODEL_NAME}' not found!")
            print(f"   Did you run './setup_model.sh' yet?")
            return
            
    except Exception as e:
        print(f"❌ Could not connect to Ollama: {e}")
        print("   Make sure Ollama is running in the background!")
        return

    print("✅ Model loaded! You can now ask questions about 10th Standard History.")
    print("   (Type 'exit' to quit)\n")

    # 2. Chat Loop
    messages = []
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 Dhanyaawad! (Thank You)")
                break

            messages.append({'role': 'user', 'content': user_input})
            
            print("Tutor: ", end="", flush=True)

            # 3. Stream Response
            stream = ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                stream=True
            )

            full_response = ""
            for chunk in stream:
                content = chunk['message']['content']
                sys.stdout.write(content)
                sys.stdout.flush()
                full_response += content

            print("\n")
            messages.append({'role': 'assistant', 'content': full_response})

        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break

if __name__ == "__main__":
    main()
