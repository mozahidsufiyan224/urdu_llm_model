# Urdu LLM Model Testing Documentation

## Overview
This documentation covers the testing script for your custom-trained Urdu Language Model (LLM). The script allows you to interactively test your model's text generation capabilities or run predefined test examples.

## Requirements

### Software Dependencies
- Python 3.8+
- PyTorch (1.12+)
- Transformers library (4.25+)
- CUDA Toolkit (if using GPU)

Install with:
```bash
pip install torch transformers
```

### Hardware Requirements
- CPU: Minimum 4 cores recommended
- RAM: 8GB minimum, 16GB recommended
- GPU: Optional but recommended (NVIDIA with CUDA support)

## Configuration

### Key Parameters
All configurable parameters are at the top of the script:

```python
MODEL_PATH = "urdu-llm"  # Path to trained model directory
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"  # Auto device selection
MAX_LENGTH = 200  # Maximum tokens to generate
TEMPERATURE = 0.7  # Range: 0.1-1.0 (lower = more deterministic)
TOP_K = 50  # Number of high-probability tokens to consider
TOP_P = 0.95  # Nucleus sampling threshold
REPETITION_PENALTY = 1.2  # Penalty for repeated phrases (1.0 = no penalty)
```

## Functions

### `load_model()`
- **Purpose**: Loads the trained model and tokenizer
- **Returns**: Tuple of (tokenizer, model)
- **Error Handling**: Catches and reports loading failures

### `generate_text(prompt, model, tokenizer)`
- **Parameters**:
  - `prompt`: Input text in Urdu
  - `model`: Loaded LLM model
  - `tokenizer`: Corresponding tokenizer
- **Returns**: Generated Urdu text
- **Generation Parameters**: Uses configured TEMPERATURE, TOP_K, etc.

### `interactive_test(tokenizer, model)`
- **Mode**: Interactive command-line interface
- **Features**:
  - Continuous prompt input
  - 'exit' command to quit
  - Input validation
  - Clean output formatting

### `test_examples(tokenizer, model)`
- **Purpose**: Run predefined test cases
- **Included Examples**:
  1. "پاکستان میں تعلیم کا نظام"
  2. "کرکٹ کھیل کے فوائد"
  3. "مصنوعی ذہانت کے استعمال"
  4. "اردو زبان کی تاریخ"

## Usage Instructions

### Basic Testing
1. Run the script:
   ```bash
   python test_urdu_llm.py
   ```
2. Enter Urdu prompts when prompted
3. Type 'exit' to quit

### Predefined Examples
Uncomment this line in `main()`:
```python
test_examples(tokenizer, model)
```

### Output Interpretation
- Generated text will appear after "تخلیق شدہ متن:"
- The script automatically removes the input prompt from output
- Lines are separated for readability

## Advanced Options

### Generation Tuning
Adjust these parameters for different results:
- **Temperature**: Higher values (0.7-1.0) for more creativity
- **Top_P**: Lower values (0.7-0.9) for more focused output
- **Repetition Penalty**: Increase (1.1-1.5) to reduce repetition

### Batch Testing
Modify the script to:
1. Read prompts from a file
2. Save outputs to log
3. Add automatic evaluation metrics

## Troubleshooting

### Common Issues
1. **Model Not Found**:
   - Verify `MODEL_PATH` points to correct directory
   - Check if these files exist:
     - config.json
     - pytorch_model.bin
     - tokenizer files

2. **Poor Generation Quality**:
   - Try lower temperature
   - Increase repetition penalty
   - Verify model was properly trained

3. **CUDA Out of Memory**:
   - Reduce MAX_LENGTH
   - Use smaller batch sizes
   - Run on CPU instead

## Sample Output
```
اردو میں سوال کریں: مصنوعی ذہانت کے استعمال

تخلیق ہو رہی ہے...

نتیجہ:
مصنوعی ذہانت کے استعمال آج کل ہر شعبہ زندگی میں بڑھ رہے ہیں۔ طبیعات سے لے کر تعلیم تک، کاروبار سے لے کر حکومتی معاملات تک، AI نے انقلاب برپا کر دیا ہے۔ پاکستان میں بھی اس ٹیکنالوجی کے استعمال میں اضافہ ہو رہا ہے، خاص طور پر زراعت اور صحت کے شعبوں میں۔
```

## License
This testing script is provided as-is for educational and research purposes. Users are responsible for ensuring their use complies with all applicable laws and model licenses.
