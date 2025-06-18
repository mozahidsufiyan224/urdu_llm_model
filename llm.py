import os
import pandas as pd
from transformers import pipeline, AutoTokenizer
import warnings
import re
from collections import Counter

# Disable all warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

class UrduLLMProcessor:
    def __init__(self):
        # Configuration
        self.articles_path = r'C:\a_llm\urdu_article\ncpul_articles_archive'
        self.output_file = 'urdu_llm_results.csv'
        
        # Define categories
        self.CATEGORY_MAP = {
            'کھیل': 'sports',
            'سائنس': 'science',
            'عالمی': 'world',
            'صحت': 'health',
            'فن و ثقافت': 'arts',
            'کاروبار': 'business',
            'ٹیکنالوجی': 'technology',
            'سیاست': 'politics',
            'دیگر': 'other'
        }
        
        # Model configuration
        self.MAX_CLASSIFICATION_TOKENS = 500
        self.MAX_SUMMARIZATION_TOKENS = 768
        self.CHUNK_OVERLAP = 30
        self.MIN_SUMMARY_LENGTH = 25
        self.MAX_SUMMARY_LENGTH = 120
        self.MIN_CHUNK_LENGTH = 150
        
        # Initialize models
        self.classifier = None
        self.summarizer = None
        self.tokenizer = None
    
    def initialize_models(self):
        """Load pre-trained models with error handling"""
        try:
            # Initialize tokenizer first
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-multilingual-cased")
            
            # For classification
            self.classifier = pipeline(
                "text-classification",
                model="distilbert-base-multilingual-cased",
                device=-1,
                tokenizer=self.tokenizer
            )
            
            # For summarization
            self.summarizer = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-12-6",
                device=-1,
                tokenizer="sshleifer/distilbart-cnn-12-6"
            )
            
            print("Models loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading models: {e}")
            return False

    def _map_to_urdu_category(self, label):
        """Map model output to Urdu categories"""
        label = str(label).lower()
        if 'sport' in label:
            return 'کھیل'
        elif 'tech' in label:
            return 'ٹیکنالوجی'
        elif 'polit' in label:
            return 'سیاست'
        elif 'health' in label:
            return 'صحت'
        elif 'science' in label:
            return 'سائنس'
        elif 'world' in label:
            return 'عالمی'
        elif 'art' in label or 'culture' in label:
            return 'فن و ثقافت'
        elif 'business' in label:
            return 'کاروبار'
        else:
            return 'دیگر'
    
    def _truncate_text_to_tokens(self, text, max_tokens):
        """Safely truncate text to specified number of tokens"""
        tokens = self.tokenizer.tokenize(text)
        if len(tokens) <= max_tokens:
            return text
        
        truncated_tokens = tokens[:max_tokens]
        return self.tokenizer.convert_tokens_to_string(truncated_tokens)
    
    def classify_text(self, text):
        """Classify Urdu text with robust error handling"""
        if not self.classifier:
            raise ValueError("Classifier not initialized")
        
        try:
            safe_text = self._truncate_text_to_tokens(text, self.MAX_CLASSIFICATION_TOKENS)
            result = self.classifier(safe_text)
            return self._map_to_urdu_category(result[0]['label'])
        except Exception as e:
            print(f"Classification failed: {str(e)[:100]}...")
            return "دیگر"
    
    def _chunk_text_for_summarization(self, text):
        """Special chunking for summarization that ensures meaningful chunks"""
        paragraphs = re.split(r'\n\s*\n', text)
        if len(paragraphs) > 1:
            chunks = []
            current_chunk = []
            current_length = 0
            
            for para in paragraphs:
                para_tokens = self.tokenizer.tokenize(para)
                para_length = len(para_tokens)
                
                if para_length > self.MAX_SUMMARIZATION_TOKENS:
                    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', para)
                    for sent in sentences:
                        sent_tokens = self.tokenizer.tokenize(sent)
                        sent_length = len(sent_tokens)
                        
                        if current_length + sent_length > self.MAX_SUMMARIZATION_TOKENS:
                            if current_chunk:
                                chunks.append(' '.join(current_chunk))
                            current_chunk = [sent]
                            current_length = sent_length
                        else:
                            current_chunk.append(sent)
                            current_length += sent_length
                else:
                    if current_length + para_length > self.MAX_SUMMARIZATION_TOKENS:
                        if current_chunk:
                            chunks.append(' '.join(current_chunk))
                        current_chunk = [para]
                        current_length = para_length
                    else:
                        current_chunk.append(para)
                        current_length += para_length
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            return chunks
        
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sent in sentences:
            sent_tokens = self.tokenizer.tokenize(sent)
            sent_length = len(sent_tokens)
            
            if current_length + sent_length > self.MAX_SUMMARIZATION_TOKENS:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sent]
                current_length = sent_length
            else:
                current_chunk.append(sent)
                current_length += sent_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _safe_summarize(self, text, max_length, min_length):
        """Wrapper for summarization with additional checks"""
        tokens = self.tokenizer.tokenize(text)
        token_count = len(tokens)
        
        if token_count < self.MIN_CHUNK_LENGTH:
            return None
        
        actual_max = min(max_length, token_count)
        actual_min = min(min_length, actual_max - 1)
        
        if actual_min >= actual_max:
            actual_min = max(10, actual_max // 2)
        
        try:
            summary = self.summarizer(
                text,
                max_length=actual_max,
                min_length=actual_min,
                do_sample=False,
                truncation=True
            )
            return summary[0]['summary_text']
        except Exception as e:
            print(f"Summarization skipped (safe mode): {str(e)[:100]}...")
            return None
    
    def summarize_text(self, text):
        """Generate summary with robust error handling"""
        if not self.summarizer:
            raise ValueError("Summarizer not initialized")
        
        tokens = self.tokenizer.tokenize(text)
        if len(tokens) <= self.MAX_SUMMARIZATION_TOKENS:
            summary = self._safe_summarize(
                text,
                self.MAX_SUMMARY_LENGTH,
                self.MIN_SUMMARY_LENGTH
            )
            if summary:
                return summary
        
        chunks = self._chunk_text_for_summarization(text)
        valid_chunks = [chunk for chunk in chunks 
                       if len(self.tokenizer.tokenize(chunk)) >= self.MIN_CHUNK_LENGTH]
        
        if not valid_chunks:
            return "خلاصہ دستیاب نہیں (متن بہت چھوٹا ہے)"
        
        chunk_summaries = []
        for chunk in valid_chunks:
            chunk_summary = self._safe_summarize(
                chunk,
                self.MAX_SUMMARY_LENGTH // len(valid_chunks),
                max(15, self.MIN_SUMMARY_LENGTH // len(valid_chunks))
            )
            if chunk_summary:
                chunk_summaries.append(chunk_summary)
        
        if not chunk_summaries:
            return "خلاصہ دستیاب نہیں"
        
        return ' '.join(chunk_summaries)
    
    def process_files(self):
        """Process all text files in the directory with progress tracking"""
        results = []
        
        if not os.path.exists(self.articles_path):
            print(f"Directory not found: {self.articles_path}")
            print(f"Please create the folder and add Urdu text files")
            return pd.DataFrame()
        
        processed_files = 0
        for root, _, files in os.walk(self.articles_path):
            for filename in files:
                if filename.endswith('.txt'):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            text = f.read().strip()
                        
                        if not text:
                            print(f"Skipping empty file: {filename}")
                            continue
                        
                        category = self.classify_text(text)
                        summary = self.summarize_text(text)
                        
                        results.append({
                            'file_name': filename,
                            'file_path': os.path.relpath(filepath, self.articles_path),
                            'category_urdu': category,
                            'category_english': self.CATEGORY_MAP.get(category, 'other'),
                            'summary': summary,
                            'text_length': len(text),
                            'text_sample': text[:100] + '...' if len(text) > 100 else text
                        })
                        
                        processed_files += 1
                        if processed_files % 5 == 0:
                            print(f"Processed {processed_files} files... Current file: {filename}")
                            
                    except Exception as e:
                        print(f"Error processing {filename}: {str(e)[:100]}...")
        
        return pd.DataFrame(results)

if __name__ == "__main__":
    processor = UrduLLMProcessor()
    
    if not processor.initialize_models():
        print("Failed to initialize models. Exiting...")
        exit()
    
    print(f"\nProcessing files in: {processor.articles_path}")
    results = processor.process_files()
    
    if not results.empty:
        results.to_csv(processor.output_file, index=False, encoding='utf-8-sig')
        print(f"\nSuccessfully processed {len(results)} files")
        print(f"Results saved to {processor.output_file}")
        print("\nSample results:")
        print(results[['file_name', 'category_urdu', 'summary']].head())
    else:
        print("\nNo files processed. Please check:")
        print(f"1. Folder exists: {processor.articles_path}")
        print("2. Contains .txt files")
        print("3. Files contain Urdu text")