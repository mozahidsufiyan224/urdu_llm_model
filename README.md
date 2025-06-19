# 1 run scarapper.py
# 2 then run ML.py to classify the document
# 3 then run llm2.py file to generate llm model
# 4 then run test_llm2.py file to test the urdu model
# Urdu Text Processing System Documentation

## Overview

This system processes Urdu text documents to perform automatic classification and summarization using transformer-based machine learning models. The system is designed to handle large collections of Urdu text files, classify them into categories, and generate summaries while managing memory constraints and text length limitations.

## System Components

### 1. Configuration

#### Class Initialization (`__init__` method)
- **Articles Path**: Location of Urdu text files to process (`C:\a_llm\urdu_article\ncpul_articles_archive`)
- **Output File**: CSV file to store results (`urdu_llm_results.csv`)
- **Category Mapping**: Urdu-to-English category mapping for 8 standard categories plus "other"
- **Model Parameters**: Token limits and length settings for processing

### 2. Model Initialization

#### `initialize_models()`
- Loads two pretrained models:
  1. **Classifier**: `distilbert-base-multilingual-cased` for text classification
  2. **Summarizer**: `sshleifer/distilbart-cnn-12-6` for text summarization
- Initializes tokenizer for Urdu text processing
- Configures both models to use CPU

### 3. Core Processing Methods

#### Text Classification
- `classify_text(text)` - Classifies Urdu text into one of 9 categories
- `_map_to_urdu_category(label)` - Maps model output labels to Urdu categories

#### Text Summarization
- `summarize_text(text)` - Generates summaries of Urdu text
- `_chunk_text_for_summarization(text)` - Splits long texts into manageable chunks
- `_safe_summarize(text, max_length, min_length)` - Safe wrapper for summarization with error handling

#### Utility Methods
- `_truncate_text_to_tokens(text, max_tokens)` - Ensures text stays within model token limits

### 4. File Processing

#### `process_files()`
- Walks through directory structure
- Processes each `.txt` file
- Handles errors gracefully
- Tracks progress (reports every 5 files)
- Returns pandas DataFrame with results

## Usage

### Basic Workflow

1. Initialize processor:
   ```python
   processor = UrduLLMProcessor()
   ```

2. Load models:
   ```python
   if not processor.initialize_models():
       print("Failed to initialize models. Exiting...")
       exit()
   ```

3. Process files:
   ```python
   results = processor.process_files()
   ```

4. Save results:
   ```python
   results.to_csv(processor.output_file, index=False, encoding='utf-8-sig')
   ```

### Input Requirements

- UTF-8 encoded Urdu text files (`.txt` extension)
- Files should contain meaningful content (empty files are skipped)
- Directory structure:
  ```
  ncpul_articles_archive/
  ├── folder1/
  │   ├── file1.txt
  │   └── file2.txt
  └── folder2/
      └── file3.txt
  ```

### Output Format

CSV file with columns:
- `file_name`: Original filename
- `file_path`: Relative path from articles directory
- `category_urdu`: Urdu category label
- `category_english`: English category label
- `summary`: Generated summary text
- `text_length`: Character count of original text
- `text_sample`: First 100 characters of text

## Error Handling

The system includes multiple layers of error handling:

1. **Model Initialization**: Checks if models load successfully
2. **Text Processing**: 
   - Skips empty files
   - Handles classification errors with fallback to "دیگر" (other)
   - Handles summarization errors with fallback messages
3. **Length Management**: 
   - Automatically truncates over-length texts
   - Skips chunks too small for meaningful summarization
4. **File Operations**: 
   - Checks if input directory exists
   - Handles file reading errors

## Performance Considerations

1. **Memory Management**:
   - Uses DistilBERT/DistilBART for lower memory requirements
   - Explicit CPU usage configuration
   - Text chunking for long documents

2. **Processing Long Texts**:
   - Classification: Truncates to 500 tokens
   - Summarization: Uses intelligent chunking with:
     - Paragraph-level splitting first
     - Sentence-level fallback
     - Word-level splitting for very long sentences

3. **Progress Tracking**:
   - Reports progress every 5 files
   - Includes current filename in progress messages

## Customization

To adapt the system:

1. **Change Paths**:
   ```python
   self.articles_path = "new/path/to/files"
   self.output_file = "new_output_filename.csv"
   ```

2. **Modify Categories**:
   Update the `CATEGORY_MAP` dictionary with new categories

3. **Adjust Processing Parameters**:
   ```python
   self.MAX_CLASSIFICATION_TOKENS = 400  # Reduce for stricter limits
   self.MAX_SUMMARY_LENGTH = 150         # Increase for longer summaries
   ```

4. **Change Models**:
   Replace model names in `initialize_models()` with compatible alternatives

## Example Output

Sample CSV output:

```csv
file_name,category_urdu,category_english,summary,text_length,text_sample
example1.txt,کھیل,sports,"خلاصہ کھیل کی خبر کے بارے میں...",1200,"کھیل کی دنیا میں نئی پیش رفت..."
example2.txt,سیاست,politics,"سیاسی صورتحال کا جائزہ...",2500,"حالیہ سیاسی تبدیلیوں کے تناظر میں..."
```

## Limitations

1. **Model Accuracy**:
   - Pretrained models may not be perfectly tuned for Urdu
   - Classification depends on English label mapping

2. **Text Length**:
   - Very long documents may receive less coherent summaries
   - Extremely short texts may not summarize well

3. **Performance**:
   - CPU-only processing may be slow for large collections
   - No parallel processing implementation

## Dependencies

- Python 3.6+
- Required packages:
  - `transformers`
  - `pandas`
  - `tensorflow` (CPU version recommended)

Install with:
```bash
pip install transformers pandas tensorflow
```
# Urdu Text Processing System Documentation

## Overview

This system provides a complete solution for processing Urdu text documents, including classification and summarization using pre-trained language models. The implementation handles Urdu text files stored in a specified directory structure and generates comprehensive output with classifications and summaries.

## Features

- **Text Classification**: Categorizes Urdu documents into predefined categories
- **Text Summarization**: Generates concise summaries of Urdu documents
- **Batch Processing**: Handles multiple files in directory structures
- **Bilingual Output**: Provides results in both Urdu and English
- **Error Handling**: Robust handling of various edge cases

## System Requirements

- Python 3.8+
- Windows/Linux/macOS
- 8GB+ RAM (16GB recommended for better performance)

## Installation

1. **Create a virtual environment** (recommended):

```bash
python -m venv urdu_env
source urdu_env/bin/activate  # On Windows: urdu_env\Scripts\activate
```

2. **Install dependencies**:

```bash
pip install transformers torch pandas tqdm
```

For GPU acceleration (optional):

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Configuration

Modify these parameters in the `UrduLLMProcessor` class initialization:

```python
self.articles_path = r'C:\a_llm\urdu_article\ncpul_articles_archive'  # Path to your Urdu documents
self.output_file = 'urdu_llm_results.csv'  # Output filename
self.CATEGORY_MAP = {  # Customize categories as needed
    'کھیل': 'sports',
    'سائنس': 'science',
    # ... other categories
}
```

## Usage

### 1. Initialize the Processor

```python
processor = UrduLLMProcessor()
```

### 2. Load Models

```python
if not processor.initialize_models():
    print("Failed to initialize models")
    # Handle error
```

### 3. Process Files

```python
results = processor.process_files()
```

### 4. Save Results

```python
results.to_csv('output.csv', index=False, encoding='utf-8-sig')
```

## Class Documentation

### `UrduLLMProcessor`

Main class that handles Urdu text processing.

#### Methods:

- `initialize_models()`: Loads pre-trained models
  - Returns: `True` if successful, `False` otherwise

- `classify_text(text)`: Classifies Urdu text
  - Parameters:
    - `text`: Urdu text to classify
  - Returns: Predicted category in Urdu

- `summarize_text(text, max_length=130)`: Generates summary
  - Parameters:
    - `text`: Urdu text to summarize
    - `max_length`: Maximum length of summary
  - Returns: Generated summary text

- `process_files()`: Processes all text files in configured directory
  - Returns: Pandas DataFrame with results

## Output Format

The system generates a CSV file with these columns:

| Column | Description |
|--------|-------------|
| `file_path` | Relative path to the source file |
| `category_urdu` | Predicted category in Urdu |
| `category_english` | Predicted category in English |
| `summary` | Generated summary of the document |
| `text_length` | Character count of original text |
| `text_sample` | First 100 characters of the document |

## Customization

### Changing Models

To use different pre-trained models, modify the `initialize_models()` method:

```python
self.classifier = pipeline(
    "text-classification",
    model="new-model-name",
    device=-1
)
```

### Adding Categories

Update the `CATEGORY_MAP` dictionary:

```python
self.CATEGORY_MAP = {
    'کھیل': 'sports',
    'نئی_قسم': 'new_category',
    # ... other categories
}
```

### Adjusting Summary Length

Change the `max_length` parameter in the `summarize_text()` call:

```python
summary = self.summarize_text(text, max_length=150)  # Longer summaries
```

## Troubleshooting

### Common Issues

1. **Model Loading Errors**:
   - Ensure internet connection is active for first-time downloads
   - Check Hugging Face model hub status

2. **Memory Errors**:
   - Reduce batch size in model configurations
   - Use smaller models

3. **Urdu Text Encoding**:
   - Ensure files are UTF-8 encoded
   - Verify proper rendering of Urdu characters

### Error Messages

| Error | Solution |
|-------|----------|
| "Directory not found" | Verify the `articles_path` exists |
| "No files processed" | Check directory contains .txt files |
| "Error loading models" | Try simpler models or check internet connection |

## Performance Considerations

- For large document collections (>1000 files), consider:
  - Processing in batches
  - Using GPU acceleration
  - Increasing system memory

- The system caches models after first use for faster subsequent runs

## Example Output

```csv
file_path,category_urdu,category_english,summary,text_length,text_sample
2024/06/کھیل_کرکٹ.txt,کھیل,sports,"پاکستان کرکٹ ٹیم نے میچ جیت لیا...",450,"پاکستان کرکٹ ٹیم نے آسٹریلیا کے خلاف..."
2024/06/ٹیکنالوجی_موبائل.txt,ٹیکنالوجی,technology,"نئی موبائل ٹیکنالوجی نے مارکیٹ میں تہلکہ مچا دیا...",620,"جدید ترین موبائل ٹیکنالوجی کے..."
```

## License

This system is open-source and available under the MIT License.
