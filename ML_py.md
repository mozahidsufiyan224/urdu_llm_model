# **Urdu Text Classifier Documentation**

## **Overview**
The `UrduTextClassifier` is a Python class designed to classify Urdu text documents into predefined categories (e.g., sports, science, politics) using Natural Language Processing (NLP) techniques. It also includes functionality to extract summaries from Urdu text using a TF-IDF-based approach.

### **Key Features**
- **Text Classification**: Uses `TfidfVectorizer` and `MultinomialNB` (Naive Bayes) to categorize Urdu text.
- **Summary Extraction**: Extracts key sentences from articles using TF-IDF scoring.
- **Preprocessing**: Includes Urdu-specific tokenization and stopword removal.
- **Batch Processing**: Processes multiple `.txt` files from a specified directory.

---

## **Class Initialization**
### **`UrduTextClassifier.__init__()`**
Initializes the classifier with:
- **Category Mapping**: Urdu-to-English category labels.
- **Urdu Stopwords**: Common stopwords to filter out.
- **Model Pipeline**: Combines `TfidfVectorizer` and `MultinomialNB`.
- **Articles Path**: Directory path where Urdu text files are stored.

#### **Parameters**
None (hardcoded paths and settings).

#### **Attributes**
| Attribute | Description |
|-----------|-------------|
| `CATEGORIES` | Dictionary mapping Urdu categories to English. |
| `STOPWORDS` | Set of common Urdu stopwords. |
| `model` | Scikit-learn pipeline (`TfidfVectorizer` + `MultinomialNB`). |
| `articles_path` | Path to the folder containing Urdu text files. |

---

## **Methods**
### **1. `tokenize_urdu(text)`**
Tokenizes Urdu text by removing punctuation and filtering stopwords.

#### **Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Input Urdu text to tokenize. |

#### **Returns**
- `list[str]`: List of cleaned Urdu tokens.

#### **Example**
```python
tokens = classifier.tokenize_urdu("کرکٹ میچ میں پاکستان نے جیت حاصل کی")
# Output: ['کرکٹ', 'میچ', 'پاکستان', 'جیت', 'حاصل']
```

---

### **2. `extract_summary(text, num_sentences=3)`**
Extracts a summary from Urdu text using TF-IDF-based sentence scoring.

#### **Parameters**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `text` | `str` | Input Urdu text. | - |
| `num_sentences` | `int` | Number of sentences in summary. | `3` |

#### **Returns**
- `str`: Extracted summary.

#### **Example**
```python
summary = classifier.extract_summary("پاکستان نے میچ جیت لیا...", num_sentences=2)
# Output: "پاکستان نے میچ جیت لیا..."
```

---

### **3. `preprocess_text(text)`**
Preprocesses Urdu text for classification by:
1. Removing punctuation.
2. Normalizing whitespace.
3. Tokenizing and removing stopwords.

#### **Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Input Urdu text. |

#### **Returns**
- `str`: Preprocessed text.

#### **Example**
```python
cleaned_text = classifier.preprocess_text("پاکستان نے میچ جیت لیا!")
# Output: "پاکستان میچ جیت لیا"
```

---

### **4. `train_classifier(labeled_data)`**
Trains the classifier using labeled Urdu text data.

#### **Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| `labeled_data` | `list[dict]` | List of dictionaries with `text` and `category`. |

#### **Example**
```python
TRAINING_DATA = [
    {'text': 'پاکستان کرکٹ ٹیم نے میچ جیت لیا', 'category': 'کھیل'},
    {'text': 'نئی ٹیکنالوجی نے مارکیٹ میں تہلکہ مچا دیا', 'category': 'ٹیکنالوجی'}
]
classifier.train_classifier(TRAINING_DATA)
```

---

### **5. `process_files()`**
Processes all `.txt` files in `articles_path` and returns a DataFrame with:
- File path
- Predicted category (Urdu & English)
- Extracted summary
- Text length
- Text sample

#### **Returns**
- `pd.DataFrame`: Structured results.

#### **Example Output**
| file_path | category_urdu | category_english | summary | text_length | text_sample |
|-----------|--------------|------------------|---------|-------------|-------------|
| `sports/1.txt` | `کھیل` | `sports` | "پاکستان نے میچ جیت لیا..." | `500` | "پاکستان نے میچ جیت لیا..." |

---

## **Example Usage**
```python
if __name__ == "__main__":
    # Initialize classifier
    classifier = UrduTextClassifier()
    
    # Sample training data
    TRAINING_DATA = [
        {'text': 'پاکستان کرکٹ ٹیم نے میچ جیت لیا', 'category': 'کھیل'},
        {'text': 'نئی ٹیکنالوجی نے مارکیٹ میں تہلکہ مچا دیا', 'category': 'ٹیکنالوجی'},
        {'text': 'وزیراعظم نے نئی پالیسی کا اعلان کیا', 'category': 'سیاست'}
    ]
    
    # Train classifier
    classifier.train_classifier(TRAINING_DATA)
    
    # Process files
    results = classifier.process_files()
    
    # Save results
    results.to_csv("urdu_articles_classified.csv", encoding="utf-8-sig")
```

---

## **Output File (`urdu_articles_classified.csv`)**
The script generates a CSV file with the following columns:
1. **`file_path`**: Relative path to the text file.
2. **`category_urdu`**: Predicted category in Urdu.
3. **`category_english`**: Predicted category in English.
4. **`summary`**: Extracted summary.
5. **`text_length`**: Character count of the text.
6. **`text_sample`**: First 100 characters of the text.

---

## **Dependencies**
| Package | Purpose |
|---------|---------|
| `pandas` | Data handling |
| `scikit-learn` | TF-IDF & Naive Bayes |
| `numpy` | Numerical operations |
| `re` | Regex for text cleaning |
| `os` | File system operations |

Install dependencies using:
```bash
pip install pandas scikit-learn numpy
```

---

## **Limitations**
1. **Small Training Data**: Performance depends on labeled data quality.
2. **Static Stopwords**: May not cover all Urdu stopwords.
3. **Sentence Splitting**: Simple regex-based splitting may fail in complex cases.
4. **BBC Urdu-Specific**: Categories are tailored for BBC Urdu content.

---

## **Future Improvements**
- **Better Tokenization**: Use `Urduhack` or `spaCy` for Urdu NLP.
- **Deep Learning**: Replace Naive Bayes with BERT-based models.
- **Dynamic Path Handling**: Allow path configuration via arguments.
- **Error Logging**: Log errors for debugging.

---

This classifier provides a basic but effective way to categorize and summarize Urdu text. Adjust the `CATEGORIES` and `STOPWORDS` for better domain-specific performance.
