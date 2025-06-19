import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from pathlib import Path

# Configuration
MODEL_PATH = "urdu-llm"  # Path to your trained model
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_LENGTH = 200  # Maximum length of generated text
TEMPERATURE = 0.7  # Controls randomness (lower = more predictable)
TOP_K = 50  # Consider top K probable tokens
TOP_P = 0.95  # Nucleus sampling probability
REPETITION_PENALTY = 1.2  # Penalize repeated text

def load_model():
    """Load the trained Urdu LLM model and tokenizer"""
    print("Loading Urdu LLM model...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
        model.to(DEVICE)
        print("Model loaded successfully!")
        return tokenizer, model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None

def generate_text(prompt, model, tokenizer):
    """Generate Urdu text from prompt"""
    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=MAX_LENGTH,
            num_return_sequences=1,
            temperature=TEMPERATURE,
            top_k=TOP_K,
            top_p=TOP_P,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=REPETITION_PENALTY
        )
    
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def interactive_test(tokenizer, model):
    """Interactive testing loop"""
    print("\nUrdu LLM Text Generation")
    print("Type your Urdu prompt and press Enter")
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            prompt = input("اردو میں سوال کریں: ")
            if prompt.lower() == 'exit':
                break
            
            if not prompt.strip():
                print("برائے مہربانی کوئی متن درج کریں\n")
                continue
                
            print("\nتخلیق ہو رہی ہے...\n")
            generated_text = generate_text(prompt, model, tokenizer)
            
            # Clean up output by removing the input prompt if it's repeated
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            print("نتیجہ:")
            print(generated_text)
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\nختم کیا جا رہا ہے...")
            break
        except Exception as e:
            print(f"خرابی: {e}")

def test_examples(tokenizer, model):
    """Run some predefined test examples"""
    examples = [
        "پاکستان میں تعلیم کا نظام",
        "کرکٹ کھیل کے فوائد",
        "مصنوعی ذہانت کے استعمال",
        "اردو زبان کی تاریخ"
    ]
    
    print("Running test examples...\n")
    for prompt in examples:
        print(f"پروامپٹ: {prompt}")
        generated_text = generate_text(prompt, model, tokenizer)
        
        # Clean up output
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        print("تخلیق شدہ متن:")
        print(generated_text)
        print("\n" + "-"*50 + "\n")

def main():
    tokenizer, model = load_model()
    if not tokenizer or not model:
        print("Model loading failed. Please check:")
        print(f"1. Model exists at {MODEL_PATH}")
        print("2. You have all required packages installed")
        return
    
    # Run interactive test
    interactive_test(tokenizer, model)
    
    # Alternatively, run predefined examples
    # test_examples(tokenizer, model)

if __name__ == "__main__":
    main()