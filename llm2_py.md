# Urdu Language Model Training System - Comprehensive Documentation

## 1. Overview

This Python script implements a complete training pipeline for developing an Urdu Language Model (LLM) using the Hugging Face Transformers library. The system processes Urdu text articles, fine-tunes a pre-trained causal language model, and saves the customized model for future use.

## 2. System Architecture

![Training Pipeline Diagram]
1. **Data Loading**: Recursively loads Urdu text files from specified directory
2. **Preprocessing**: Cleans and tokenizes text data
3. **Model Setup**: Initializes base model and tokenizer
4. **Training**: Fine-tunes model on Urdu corpus
5. **Saving**: Persists trained model and tokenizer

## 3. Configuration Parameters

### Core Settings
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `DATA_DIR` | str | `C:\a_llm\urdu_article\ncpul_articles_archive` | Path to Urdu articles directory |
| `MODEL_NAME` | str | `urdu-llm` | Output directory for trained model |
| `PRETRAINED_MODEL` | str | `facebook/opt-350m` | Base model identifier |

### Training Hyperparameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `BLOCK_SIZE` | int | 256 | Maximum sequence length |
| `BATCH_SIZE` | int | 4 | Training batch size |
| `LEARNING_RATE` | float | 5e-5 | Initial learning rate |
| `EPOCHS` | int | 3 | Number of training epochs |

## 4. Core Functions

### `setup_environment()`
- **Purpose**: Configures runtime environment
- **Operations**:
  - Disables oneDNN warnings
  - Handles Hugging Face authentication for gated models
- **Error Handling**: Gracefully falls back to local ops if login fails

### `load_urdu_articles()`
- **Input**: None (reads from `DATA_DIR`)
- **Output**: Hugging Face `Dataset` object
- **Process**:
  1. Recursively scans directory for `.txt` files
  2. Reads content with UTF-8 encoding
  3. Performs basic cleaning
  4. Returns structured dataset
- **Error Handling**: Skips corrupt files with warning

### Training Pipeline (`main()`)
1. **Initialization**:
   - Sets up environment
   - Loads Urdu dataset
   - Initializes tokenizer (adds padding token if missing)

2. **Model Preparation**:
   - Loads pre-trained model
   - Resizes token embeddings
   - Moves to GPU if available

3. **Data Processing**:
   - Tokenizes text with parallel processing
   - Removes original text columns
   - Chunks into `BLOCK_SIZE` sequences

4. **Training**:
   - Configures training arguments
   - Sets up `Trainer` with:
     - Model
     - Training arguments
     - Data collator (language modeling)
   - Executes training loop
   - Saves final model

## 5. Usage Guide

### Installation
```bash
pip install torch transformers datasets
```

### Execution
```bash
python train_urdu_llm.py
```

### Customization Options
1. **Model Selection**:
   ```python
   PRETRAINED_MODEL = "facebook/opt-1.3b"  # Larger model
   ```

2. **Training Configuration**:
   ```python
   EPOCHS = 5
   BATCH_SIZE = 8  # If GPU memory allows
   ```

3. **Advanced Options**:
   ```python
   training_args = TrainingArguments(
       ...,
       gradient_accumulation_steps=2,  # For larger effective batch size
       warmup_steps=500,  # Learning rate warmup
   )
   ```

## 6. Expected Output Structure

```
urdu-llm/
├── config.json
├── pytorch_model.bin
├── training_args.bin
└── tokenizer_config.json
logs/
├── events.out.tfevents...  # Training logs
```

## 7. Best Practices

### Data Preparation
- Ensure text files are clean UTF-8 encoded
- Recommended structure:
  ```
  ncpul_articles_archive/
  ├── year/
  │   ├── month/
  │   │   ├── article1.txt
  ```

### Performance Tuning
- For GPUs with <12GB VRAM:
  ```python
  BATCH_SIZE = 2
  BLOCK_SIZE = 128
  ```

- For multi-GPU training:
  ```python
  training_args = TrainingArguments(
      ...,
      dataloader_num_workers=4,
      fp16=True,
  )
  ```

## 8. Troubleshooting

### Common Issues
| Symptom | Solution |
|---------|----------|
| CUDA Out of Memory | Reduce batch size/block size |
| Tokenization Errors | Verify text encoding is UTF-8 |
| Slow Training | Enable FP16 (`fp16=True`) |
| Poor Convergence | Adjust learning rate (3e-5 to 5e-5) |

### Log Interpretation
- Training logs appear in `./logs`
- Monitor loss trends:
  - Steady decrease: Good learning
  - Fluctuations: Reduce learning rate
  - Plateau: More data/epochs needed

## 9. License & Compliance

- **License**: MIT
- **Model Compliance**: User responsible for ensuring:
  - Base model license adherence
  - Data usage rights
  - Ethical AI deployment

## 10. Extension Points

1. **Add Validation**:
   ```python
   training_args = TrainingArguments(
       ...,
       evaluation_strategy="epoch",
       eval_steps=500,
   )
   ```

2. **Custom Tokenizer**:
   ```python
   tokenizer = AutoTokenizer.from_pretrained(
       PRETRAINED_MODEL,
       use_fast=False  # For custom tokenizers
   )
   ```

3. **Callbacks**:
   ```python
   from transformers import EarlyStoppingCallback
   trainer = Trainer(
       ...,
       callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
   )
   ```

This documentation provides complete coverage of the training system. For optimal results, ensure your Urdu corpus is high-quality and representative of your target domain.
