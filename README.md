# 1 run scarapper.py
# 2 then run ML.py to classify the document
# 3 then run llm.py file to generate llm model
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
