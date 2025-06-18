import os
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import numpy as np

class UrduTextClassifier:
    def __init__(self):
        # Category mapping
        self.CATEGORIES = {
            'کھیل': 'sports',
            'سائنس': 'science',
            'عالمی': 'world',
            'صحت': 'health',
            'فن و ثقافت': 'arts',
            'کاروبار': 'business',
            'ٹیکنالوجی': 'technology',
            'سیاست': 'politics'
        }
        
        # Urdu stopwords
        self.STOPWORDS = set([
            'اور', 'ہے', 'کی', 'ہےں', 'ہوں', 'سے', 'کو', 'میں', 'کے', 'لیے',
            'ہیں', 'تھا', 'تھی', 'تھے', 'کر', 'گی', 'گا', 'گے', 'نے', 'یہ',
            'اس', 'وہ', 'آپ', 'کہ', 'یا', 'تو', 'پر', 'بھی', 'ہی', 'ہو'
        ])
        
        # Initialize classifier
        self.model = make_pipeline(
            TfidfVectorizer(tokenizer=self.tokenize_urdu),
            MultinomialNB()
        )
        
        # Set the specific path
        self.articles_path = r'C:\a_llm\urdu_article\ncpul_articles_archive'
    
    def tokenize_urdu(self, text):
        """Basic Urdu tokenizer without external dependencies"""
        text = re.sub(r'[^\w\u0600-\u06FF\s]', ' ', text)
        words = re.findall(r'[\w\u0600-\u06FF]+', text)
        return [word for word in words if word not in self.STOPWORDS]
    
    def extract_summary(self, text, num_sentences=3):
        """Extract key sentences as summary using TF-IDF approach"""
        # Simple Urdu sentence splitting
        sentences = re.split(r'[.!؟]+\s*', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= num_sentences:
            return text
            
        # Preprocess each sentence
        preprocessed = [self.preprocess_text(sent) for sent in sentences]
        
        # Create TF-IDF matrix
        vectorizer = TfidfVectorizer(tokenizer=self.tokenize_urdu)
        sentence_vectors = vectorizer.fit_transform(preprocessed)
        
        # Calculate sentence importance scores
        scores = np.array(sentence_vectors.sum(axis=1)).flatten()
        
        # Rank sentences and pick top ones
        ranked_indices = np.argsort(-scores)
        top_indices = sorted(ranked_indices[:num_sentences])
        
        # Return summary in original order
        return ' '.join([sentences[i] for i in top_indices])
    
    def preprocess_text(self, text):
        """Text preprocessing for classification"""
        text = re.sub(r'[^\w\u0600-\u06FF\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return ' '.join(self.tokenize_urdu(text))
    
    def train_classifier(self, labeled_data):
        """Train classifier with labeled data"""
        df = pd.DataFrame(labeled_data)
        X = df['text']
        y = df['category'].map(lambda x: self.CATEGORIES.get(x, 'other'))
        self.model.fit(X, y)
    
    def process_files(self):
        """Process all text files in the specified path"""
        results = []
        
        if not os.path.exists(self.articles_path):
            print(f"Folder not found: {self.articles_path}")
            return pd.DataFrame()
        
        for root, _, files in os.walk(self.articles_path):
            for filename in files:
                if filename.endswith('.txt'):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            text = f.read()
                        
                        # Extract summary
                        summary = self.extract_summary(text)
                        
                        # Predict category
                        predicted_en = self.model.predict([text])[0]
                        predicted_urdu = next(
                            (k for k, v in self.CATEGORIES.items() if v == predicted_en),
                            'دیگر'
                        )
                        
                        rel_path = os.path.relpath(filepath, self.articles_path)
                        
                        results.append({
                            'file_path': rel_path,
                            'category_urdu': predicted_urdu,
                            'category_english': predicted_en,
                            'summary': summary,
                            'text_length': len(text),
                            'text_sample': text[:100] + '...'
                        })
                    except Exception as e:
                        print(f"Error processing {filename}: {str(e)}")
        
        return pd.DataFrame(results)

# Example Usage
if __name__ == "__main__":
    # Initialize classifier
    classifier = UrduTextClassifier()
    
    # Sample training data
    TRAINING_DATA = [
        {'text': 'پاکستان کرکٹ ٹیم نے میچ جیت لیا', 'category': 'کھیل'},
        {'text': 'نئی ٹیکنالوجی نے مارکیٹ میں تہلکہ مچا دیا', 'category': 'ٹیکنالوجی'},
        {'text': 'وزیراعظم نے نئی پالیسی کا اعلان کیا', 'category': 'سیاست'},
        {'text': 'ہسپتالوں میں نئے آلات کی تنصیب', 'category': 'صحت'},
        {'text': 'نئی فلم نے باکس آفس پر ریکارڈ توڑ دیے', 'category': 'فن و ثقافت'},
        {'text': 'اسٹاک مارکیٹ میں تیزی', 'category': 'کاروبار'},
        {'text': 'نئی سائنسی تحقیق', 'category': 'سائنس'},
        {'text': 'عالمی کانفرنس میں شرکاء', 'category': 'عالمی'}
    ]
    
    # Train classifier
    print("Training classifier...")
    classifier.train_classifier(TRAINING_DATA)
    
    # Process files
    print(f"\nProcessing files in: {classifier.articles_path}")
    results = classifier.process_files()
    
    # Save and display results
    if not results.empty:
        output_file = 'urdu_articles_classified.csv'
        results.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\nResults saved to {output_file}")
        print("\nSample output:")
        print(results[['file_path', 'category_urdu', 'summary']].head())
    else:
        print("\nNo files processed. Please check:")
        print(f"1. Folder exists: {classifier.articles_path}")
        print("2. Contains .txt files")
        print("3. Files contain Urdu text")