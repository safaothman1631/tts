"""
NLP Processing Module for Text-to-Speech
Handles text normalization, entity recognition, sentiment analysis, and language detection
"""

import re
import nltk
from textblob import TextBlob
from langdetect import detect, LangDetectException
import inflect
from num2words import num2words
from config import ABBREVIATIONS, KURDISH_ABBREVIATIONS, ENABLE_NER, ENABLE_SENTIMENT, DEFAULT_LANGUAGE

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class NLPProcessor:
    """
    Advanced NLP processor for text preparation before TTS conversion
    """
    
    def __init__(self):
        self.inflect_engine = inflect.engine()
        self.language = DEFAULT_LANGUAGE
        
    def detect_language(self, text):
        """Detect the language of the input text"""
        try:
            self.language = detect(text)
            return self.language
        except LangDetectException:
            return DEFAULT_LANGUAGE
    
    def normalize_text(self, text):
        """Normalize text by handling abbreviations, numbers, and special characters"""
        # Expand abbreviations based on language
        if self.language == 'ku':
            for abbr, full in KURDISH_ABBREVIATIONS.items():
                text = text.replace(abbr, full)
        else:
            for abbr, full in ABBREVIATIONS.items():
                text = re.sub(r'\b' + re.escape(abbr), full, text, flags=re.IGNORECASE)
        
        # Convert numbers to words
        text = self._convert_numbers_to_words(text)
        
        # Handle special characters
        text = self._process_special_characters(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _convert_numbers_to_words(self, text):
        """Convert numeric values to word representation"""
        # Kurdish number conversion
        if self.language == 'ku':
            return self._convert_kurdish_numbers(text)
        
        # Handle currency
        text = re.sub(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', 
                     lambda m: f"{num2words(float(m.group(1).replace(',', '')), to='currency', currency='USD')}", 
                     text)
        
        # Handle percentages
        text = re.sub(r'(\d+(?:\.\d+)?)%', 
                     lambda m: f"{num2words(float(m.group(1)))} percent", 
                     text)
        
        # Handle years (1900-2099)
        text = re.sub(r'\b(19|20)\d{2}\b',
                     lambda m: num2words(int(m.group(0)), to='year'),
                     text)
        
        # Handle ordinal numbers (1st, 2nd, 3rd, etc.)
        text = re.sub(r'\b(\d+)(st|nd|rd|th)\b',
                     lambda m: num2words(int(m.group(1)), to='ordinal'),
                     text)
        
        # Handle regular numbers
        text = re.sub(r'\b\d+\b',
                     lambda m: num2words(int(m.group(0))),
                     text)
        
        return text
    
    def _convert_kurdish_numbers(self, text):
        """Convert numbers to Kurdish words"""
        kurdish_numbers = {
            '0': 'سفر',
            '1': 'یەک',
            '2': 'دوو',
            '3': 'سێ',
            '4': 'چوار',
            '5': 'پێنج',
            '6': 'شەش',
            '7': 'حەوت',
            '8': 'هەشت',
            '9': 'نۆ',
            '10': 'دە',
            '20': 'بیست',
            '30': 'سی',
            '40': 'چل',
            '50': 'پەنجا',
            '60': 'شەست',
            '70': 'حەفتا',
            '80': 'هەشتا',
            '90': 'نەوەد',
            '100': 'سەد',
            '1000': 'هەزار',
        }
        
        # Convert simple numbers (0-10)
        for num, word in kurdish_numbers.items():
            text = re.sub(r'\b' + num + r'\b', word, text)
        
        # Handle percentage in Kurdish
        text = re.sub(r'(\d+)%', lambda m: f"{m.group(1)} لە سەدی", text)
        
        return text
    
    def _process_special_characters(self, text):
        """Handle special characters and symbols"""
        replacements = {
            '&': ' and ',
            '@': ' at ',
            '#': ' hash ',
            '%': ' percent ',
            '+': ' plus ',
            '=': ' equals ',
            '<': ' less than ',
            '>': ' greater than ',
            '|': ' or ',
            '~': ' tilde ',
            '^': ' caret ',
        }
        
        for char, word in replacements.items():
            text = text.replace(char, word)
        
        return text
    
    def segment_sentences(self, text):
        """Segment text into sentences using NLTK"""
        sentences = nltk.sent_tokenize(text)
        return sentences
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of the text"""
        if not ENABLE_SENTIMENT:
            return {"polarity": 0.0, "subjectivity": 0.0, "emotion": "neutral"}
        
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Determine emotion based on polarity
        if polarity > 0.3:
            emotion = "happy"
        elif polarity < -0.3:
            emotion = "sad"
        elif abs(polarity) < 0.1:
            emotion = "neutral"
        else:
            emotion = "neutral"
        
        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "emotion": emotion
        }
    
    def extract_entities(self, text):
        """Extract named entities from text"""
        if not ENABLE_NER:
            return []
        
        blob = TextBlob(text)
        entities = []
        
        # Get noun phrases as basic entities
        for np in blob.noun_phrases:
            entities.append({
                "text": np,
                "type": "NOUN_PHRASE"
            })
        
        return entities
    
    def add_pauses(self, text):
        """Add appropriate pauses based on punctuation"""
        # Add pauses after punctuation for natural speech
        text = re.sub(r'([.!?])', r'\1 ', text)
        text = re.sub(r'([,;:])', r'\1 ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def process_text(self, text):
        """
        Complete text processing pipeline
        Returns processed text and metadata
        """
        # Detect language
        language = self.detect_language(text)
        
        # Normalize text
        normalized_text = self.normalize_text(text)
        
        # Segment into sentences
        sentences = self.segment_sentences(normalized_text)
        
        # Analyze sentiment for entire text
        sentiment = self.analyze_sentiment(text)
        
        # Extract entities
        entities = self.extract_entities(text)
        
        # Add pauses
        final_text = self.add_pauses(normalized_text)
        
        metadata = {
            "language": language,
            "sentiment": sentiment,
            "entities": entities,
            "sentence_count": len(sentences),
            "original_length": len(text),
            "processed_length": len(final_text)
        }
        
        return final_text, metadata
