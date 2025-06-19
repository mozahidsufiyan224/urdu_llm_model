import os
from pathlib import Path
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
import torch

# Configuration - UPDATE THESE VALUES
DATA_DIR = r"C:\a_llm\urdu_article\ncpul_articles_archive"
MODEL_NAME = "urdu-llm"
PRETRAINED_MODEL = "facebook/opt-350m"  # No authentication needed
BLOCK_SIZE = 256
BATCH_SIZE = 4
LEARNING_RATE = 5e-5
EPOCHS = 3

def setup_environment():
    """Configure environment settings"""
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    
    # Only try to login if token exists and is needed
    if PRETRAINED_MODEL.startswith("meta-llama/"):  # Only needed for gated models
        hf_token = os.getenv('HF_TOKEN')
        if hf_token:
            from huggingface_hub import login
            try:
                login(token=hf_token)
                print("Successfully logged in to Hugging Face Hub")
            except Exception as e:
                print(f"Warning: Could not login to Hugging Face Hub - {e}")
                print("Continuing with local operations only")

def load_urdu_articles():
    """Load all Urdu articles from text files"""
    urdu_texts = []
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith('.txt'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Clean content as needed
                        urdu_texts.append(content)
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    print(f"Loaded {len(urdu_texts)} Urdu articles")
    return Dataset.from_dict({"text": urdu_texts})

def main():
    # Setup environment (without mandatory login)
    setup_environment()
    
    # Load and prepare data
    print("Loading Urdu articles...")
    dataset = load_urdu_articles()
    
    # Initialize tokenizer and model
    print("Initializing model...")
    tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({'pad_token': '[PAD]'})
    
    model = AutoModelForCausalLM.from_pretrained(PRETRAINED_MODEL)
    model.resize_token_embeddings(len(tokenizer))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    # Tokenize dataset
    print("Preparing dataset...")
    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, max_length=BLOCK_SIZE)
    
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text"],
        num_proc=4
    )
    
    # Train model
    print("Starting training...")
    training_args = TrainingArguments(
        output_dir=MODEL_NAME,
        overwrite_output_dir=True,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        save_steps=10_000,
        save_total_limit=2,
        logging_dir='./logs',
        logging_steps=500,
        learning_rate=LEARNING_RATE,
        fp16=device == "cuda",
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False
        ),
    )
    
    trainer.train()
    trainer.save_model(MODEL_NAME)
    tokenizer.save_pretrained(MODEL_NAME)
    print(f"Training complete! Model saved to {MODEL_NAME}")

if __name__ == "__main__":
    main()