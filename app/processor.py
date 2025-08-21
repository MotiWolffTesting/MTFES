import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import Counter
import re

class TextProcessor:
    "Processing text"
    def __init__(self, weapon_file_path="data/weapons.txt"):
        try:
            # Trying to download the nltk data
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('punkt', quiet=True)
        except Exception:
            pass
        
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.weapon_list = self._load_weapons(weapon_file_path)
        
    def _load_weapons(self, file_path):
        "Load weapon blacklist from file"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                weapons = [line.strip().lower() for line in f if line.strip()]
            return weapons
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
        
    def find_rarest_word(self, text):
        "Find rarest word in the text"
        if not text or not isinstance(text, str):
            return ""
        
        # Clean text
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if not words:
            return ""
        
        # Count words frequencies
        word_counts = Counter(words)
        
        # Find rarest word (lowered)
        if word_counts:
            rarest_word = min(word_counts.items(), key=lambda x: x[1])[0]
            return rarest_word
        return ""
    
    def analyze_sentiment(self, text):
        "Analyze sentiment of the text"
        if not text or not isinstance(text, str):
            return ""
        
        try:
            scores = self.sentiment_analyzer.polarity_scores(text)
            compund_score = scores['compound']
            
            if compund_score >= 0.5:
                return "positive"
            elif compund_score <= -0.5:
                return "negative"
            else:
                return "neutral"
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return "neutral"
        
    def detect_weapons(self, text):
        "Detect weapons from blacklist in the text"
        if not text or not isinstance(text, str):
            return ""
        
        text_lower = text.lower()
        
        for weapon in self.weapon_list:
            if weapon in text_lower:
                return weapon
        return ""
    
    def process_dataframe(self, df):
        "Process the entire df and add features"
        if df.empty:
            return df
        
        # Ensure having required columns
        if 'original_text' not in df.columns:
            print("Error: 'original_text' column not found in dataframe")
            return df
        
        # Copying to not change original
        processed_df = df.copy()
        
        # Add new features
        processed_df['rarest_word'] = processed_df['original_text'].apply(self.find_rarest_word)
        processed_df['sentiment'] = processed_df['original_text'].apply(self.analyze_sentiment)
        processed_df['weapons_detected'] = processed_df['original_text'].apply(self.detect_weapons)
        
        print(f"Successfully processed {len(processed_df)} records")
        return processed_df
        