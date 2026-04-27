"""
Text-to-Speech Engine Module
Handles audio generation with emotion-based prosody control
"""

import os
import pyttsx3
from gtts import gTTS
from pathlib import Path
from config import (
    TTS_ENGINE, VOICE_RATE, VOICE_VOLUME, VOICE_GENDER,
    EMOTION_SETTINGS, OUTPUT_DIR, AUDIO_FORMAT
)


class TTSEngine:
    """
    Text-to-Speech Engine with multiple backend support and prosody control
    """
    
    def __init__(self, engine_type=TTS_ENGINE):
        self.engine_type = engine_type
        self.output_dir = Path(OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
        
        if self.engine_type == "pyttsx3":
            self.engine = pyttsx3.init()
            self._configure_pyttsx3()
        else:
            self.engine = None
    
    def _configure_pyttsx3(self):
        """Configure pyttsx3 engine with default settings"""
        self.engine.setProperty('rate', VOICE_RATE)
        self.engine.setProperty('volume', VOICE_VOLUME)
        
        # Set voice based on gender preference
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if VOICE_GENDER.lower() in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    def adjust_for_emotion(self, emotion):
        """Adjust voice properties based on detected emotion"""
        if self.engine_type != "pyttsx3" or emotion not in EMOTION_SETTINGS:
            return
        
        settings = EMOTION_SETTINGS[emotion]
        self.engine.setProperty('rate', settings['rate'])
        self.engine.setProperty('volume', settings['volume'])
        # Note: pitch adjustment is limited in pyttsx3
    
    def speak(self, text, emotion="neutral", language="en"):
        """Convert text to speech and play it"""
        if self.engine_type == "pyttsx3":
            self.adjust_for_emotion(emotion)
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            # Use gTTS for online TTS with language support
            # Map Kurdish to supported gTTS language codes
            lang_map = {'ku': 'ar', 'en': 'en', 'ar': 'ar'}  # Kurdish uses Arabic TTS
            gtts_lang = lang_map.get(language, 'en')
            
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            temp_file = self.output_dir / "temp_speech.mp3"
            tts.save(str(temp_file))
            
            # Play the audio file
            try:
                os.system(f'start {temp_file}')  # Windows
            except:
                print(f"Audio saved to: {temp_file}")
    
    def save_to_file(self, text, filename, emotion="neutral", language="en"):
        """Convert text to speech and save to file"""
        filepath = self.output_dir / f"{filename}.{AUDIO_FORMAT}"
        
        if self.engine_type == "pyttsx3":
            self.adjust_for_emotion(emotion)
            self.engine.save_to_file(text, str(filepath))
            self.engine.runAndWait()
        else:
            # Use gTTS with language support
            lang_map = {'ku': 'ar', 'en': 'en', 'ar': 'ar'}
            gtts_lang = lang_map.get(language, 'en')
            
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            tts.save(str(filepath))
        
        return filepath
    
    def get_available_voices(self):
        """Get list of available voices"""
        if self.engine_type == "pyttsx3" and self.engine:
            voices = self.engine.getProperty('voices')
            return [{"id": v.id, "name": v.name, "languages": v.languages} for v in voices]
        return []
    
    def set_voice(self, voice_id):
        """Set specific voice by ID"""
        if self.engine_type == "pyttsx3" and self.engine:
            self.engine.setProperty('voice', voice_id)
    
    def set_rate(self, rate):
        """Set speech rate"""
        if self.engine_type == "pyttsx3" and self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume):
        """Set volume level"""
        if self.engine_type == "pyttsx3" and self.engine:
            self.engine.setProperty('volume', volume)
