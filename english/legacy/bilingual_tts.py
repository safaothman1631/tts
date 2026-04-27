"""
Bilingual TTS - English & Kurdish
سیستەمی TTS دوو زمانە - ئینگلیزی و کوردی

Supports:
- English (high quality)
- Kurdish (via pronunciation system)
- Auto language detection
- Mixed language text
"""

from gtts import gTTS
import pyttsx3
import os
import re

# Import Kurdish pronunciation if available
try:
    from kurdish_pronunciation import convert_kurdish_to_phonetic
    KURDISH_SUPPORT = True
except ImportError:
    KURDISH_SUPPORT = False
    print("⚠️ Kurdish pronunciation module not found")


class BilingualTTS:
    def __init__(self):
        self.output_dir = "output"
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        print("=" * 60)
        print("🌍 Bilingual TTS System")
        print("   English 🇬🇧 + Kurdish 🇹🇯")
        print("=" * 60)
    
    def detect_language(self, text):
        """Detect if text is English or Kurdish"""
        # Kurdish characters
        kurdish_chars = set('ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ')
        
        # Count Kurdish characters
        kurdish_count = sum(1 for c in text if c in kurdish_chars)
        total_letters = sum(1 for c in text if c.isalpha() or c in kurdish_chars)
        
        if total_letters == 0:
            return 'en'
        
        kurdish_ratio = kurdish_count / total_letters
        
        if kurdish_ratio > 0.3:
            return 'ku'
        return 'en'
    
    def speak_english(self, text, save_file=None, slow=False):
        """Speak English text"""
        print(f"\n🇬🇧 English: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        try:
            tts = gTTS(text=text, lang='en', slow=slow)
            
            if save_file:
                filepath = os.path.join(self.output_dir, save_file)
            else:
                filepath = os.path.join(self.output_dir, "temp_en.mp3")
            
            tts.save(filepath)
            os.system(f'start {filepath}')
            print(f"✅ Saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def speak_kurdish(self, text, save_file=None):
        """Speak Kurdish text using pronunciation conversion"""
        print(f"\n🇹🇯 Kurdish: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        if KURDISH_SUPPORT:
            # Convert to phonetic English
            phonetic = convert_kurdish_to_phonetic(text)
            print(f"🔤 Phonetic: {phonetic[:50]}{'...' if len(phonetic) > 50 else ''}")
        else:
            phonetic = text
        
        try:
            # Use English TTS for phonetic text
            tts = gTTS(text=phonetic, lang='en', slow=False)
            
            if save_file:
                filepath = os.path.join(self.output_dir, save_file)
            else:
                filepath = os.path.join(self.output_dir, "temp_ku.mp3")
            
            tts.save(filepath)
            os.system(f'start {filepath}')
            print(f"✅ Saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def speak(self, text, save_file=None, language=None):
        """
        Speak text with auto language detection
        
        Args:
            text (str): Text to speak
            save_file (str): Optional filename to save
            language (str): 'en' or 'ku', auto-detect if None
        """
        if language is None:
            language = self.detect_language(text)
        
        if language == 'ku':
            return self.speak_kurdish(text, save_file)
        else:
            return self.speak_english(text, save_file)
    
    def speak_mixed(self, text, save_file=None):
        """
        Speak mixed English/Kurdish text
        Splits by language and speaks each part
        """
        print(f"\n🌍 Mixed text: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        # Split text into parts by language
        parts = self._split_by_language(text)
        
        audio_files = []
        for i, (lang, part_text) in enumerate(parts):
            filename = f"temp_part_{i}.mp3"
            if lang == 'ku':
                self.speak_kurdish(part_text, filename)
            else:
                self.speak_english(part_text, filename)
            audio_files.append(os.path.join(self.output_dir, filename))
        
        return audio_files
    
    def _split_by_language(self, text):
        """Split text into language segments"""
        parts = []
        current_text = ""
        current_lang = None
        
        kurdish_chars = set('ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ')
        
        for char in text:
            if char in kurdish_chars:
                char_lang = 'ku'
            elif char.isalpha():
                char_lang = 'en'
            else:
                # Punctuation/space - keep with current language
                current_text += char
                continue
            
            if current_lang is None:
                current_lang = char_lang
            
            if char_lang != current_lang and current_text.strip():
                parts.append((current_lang, current_text.strip()))
                current_text = ""
                current_lang = char_lang
            
            current_text += char
        
        if current_text.strip():
            parts.append((current_lang or 'en', current_text.strip()))
        
        return parts
    
    def read_story(self, text, language=None):
        """Read a story with natural pauses"""
        sentences = re.split(r'[.!?،؟]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        print(f"\n📖 Reading {len(sentences)} sentences...")
        
        import time
        for i, sentence in enumerate(sentences, 1):
            print(f"\n[{i}/{len(sentences)}]")
            self.speak(sentence + ".", language=language)
            time.sleep(2)
        
        print("\n✅ Finished reading!")


def demo():
    """Demo bilingual TTS"""
    tts = BilingualTTS()
    
    print("\n" + "=" * 60)
    print("🎬 Bilingual TTS Demo")
    print("=" * 60)
    
    # English examples
    print("\n\n📚 English Examples:")
    print("-" * 40)
    
    english_texts = [
        "Hello! Welcome to our text to speech system.",
        "This is a demonstration of English voice synthesis.",
        "The weather is beautiful today."
    ]
    
    for i, text in enumerate(english_texts, 1):
        tts.speak_english(text, f"demo_english_{i}.mp3")
        import time
        time.sleep(3)
    
    # Kurdish examples
    print("\n\n📚 Kurdish Examples:")
    print("-" * 40)
    
    kurdish_texts = [
        "سڵاو چۆنیت براکەم؟",
        "ئەمڕۆ ڕۆژێکی جوانە.",
        "من زۆر خۆشحاڵم."
    ]
    
    for i, text in enumerate(kurdish_texts, 1):
        tts.speak_kurdish(text, f"demo_kurdish_{i}.mp3")
        import time
        time.sleep(3)
    
    print("\n\n✅ Demo Complete!")


def interactive():
    """Interactive bilingual TTS"""
    tts = BilingualTTS()
    
    print("\n" + "-" * 40)
    print("Type text in English or Kurdish")
    print("Commands: 'en' = English, 'ku' = Kurdish, 'quit' = Exit")
    print("-" * 40)
    
    current_lang = None  # Auto-detect
    
    while True:
        text = input("\n➤ ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye! خواحافیز!")
            break
        elif text.lower() == 'en':
            current_lang = 'en'
            print("🇬🇧 Switched to English")
            continue
        elif text.lower() == 'ku':
            current_lang = 'ku'
            print("🇹🇯 Switched to Kurdish")
            continue
        elif text.lower() == 'auto':
            current_lang = None
            print("🌍 Auto-detect enabled")
            continue
        
        if text:
            tts.speak(text, language=current_lang)


# Quick functions
def say_english(text, save_file=None):
    """Quick English TTS"""
    tts = BilingualTTS()
    return tts.speak_english(text, save_file)

def say_kurdish(text, save_file=None):
    """Quick Kurdish TTS"""
    tts = BilingualTTS()
    return tts.speak_kurdish(text, save_file)

def say(text, save_file=None):
    """Quick auto-detect TTS"""
    tts = BilingualTTS()
    return tts.speak(text, save_file)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🌍 Bilingual TTS - English & Kurdish")
    print("=" * 60)
    
    print("\nOptions:")
    print("  1. Demo")
    print("  2. Interactive mode")
    print("  3. Test English")
    print("  4. Test Kurdish")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        demo()
    elif choice == '2':
        interactive()
    elif choice == '3':
        say_english("Hello! This is a test of the English text to speech system.")
    elif choice == '4':
        say_kurdish("سڵاو! ئەمە تاقیکردنەوەی سیستەمی دەق بۆ دەنگی کوردییە.")
    else:
        interactive()
