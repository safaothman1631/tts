"""
Configuration settings for TTS with NLP Pipeline
"""

# TTS Engine Settings
TTS_ENGINE = "pyttsx3"  # Options: "pyttsx3", "gtts"
VOICE_RATE = 150  # Speech rate (words per minute)
VOICE_VOLUME = 0.9  # Volume level (0.0 to 1.0)
VOICE_GENDER = "female"  # Options: "male", "female"

# NLP Settings
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "ku", "ar"]  # English, Kurdish, Arabic
ENABLE_NER = True  # Named Entity Recognition
ENABLE_SENTIMENT = True  # Sentiment Analysis
ENABLE_PUNCTUATION_PROCESSING = True

# Text Processing Settings
MAX_SENTENCE_LENGTH = 200
ABBREVIATIONS = {
    "Dr.": "Doctor",
    "Mr.": "Mister",
    "Mrs.": "Misses",
    "Ms.": "Miss",
    "Prof.": "Professor",
    "Sr.": "Senior",
    "Jr.": "Junior",
    "etc.": "etcetera",
    "e.g.": "for example",
    "i.e.": "that is",
}

# Kurdish abbreviations and expansions
KURDISH_ABBREVIATIONS = {
    "د.": "دکتۆر",
    "پ.": "پرۆفیسۆر",
    "م.": "مامۆستا",
    "ک.": "کاک",
    "خ.": "خاتوو",
}

# Emotion-based prosody adjustments
EMOTION_SETTINGS = {
    "happy": {"rate": 170, "volume": 1.0, "pitch": 1.2},
    "sad": {"rate": 130, "volume": 0.7, "pitch": 0.8},
    "angry": {"rate": 180, "volume": 1.0, "pitch": 1.3},
    "neutral": {"rate": 150, "volume": 0.9, "pitch": 1.0},
}

# Output Settings
OUTPUT_DIR = "output"
AUDIO_FORMAT = "mp3"
SAVE_PROCESSED_TEXT = True
