"""
English Text-to-Speech System
سیستەمی دەق بۆ دەنگی ئینگلیزی

Features:
- High quality English voice using gTTS
- Offline support with pyttsx3
- Multiple voice options (male/female)
- Speed and pitch control
- Save to file or play directly
"""

from gtts import gTTS
import pyttsx3
import os

class EnglishTTS:
    def __init__(self, use_online=True):
        """
        Initialize English TTS
        
        Args:
            use_online (bool): True for gTTS (online), False for pyttsx3 (offline)
        """
        self.use_online = use_online
        self.output_dir = "output"
        
        # Create output directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Initialize offline engine
        if not use_online:
            self.engine = pyttsx3.init()
            self._setup_offline_engine()
        
        print("=" * 60)
        print("🎤 English Text-to-Speech System")
        print(f"   Mode: {'Online (gTTS)' if use_online else 'Offline (pyttsx3)'}")
        print("=" * 60)
    
    def _setup_offline_engine(self):
        """Setup pyttsx3 engine settings"""
        # Set rate (speed)
        self.engine.setProperty('rate', 150)
        
        # Set volume
        self.engine.setProperty('volume', 1.0)
        
        # Get available voices
        voices = self.engine.getProperty('voices')
        self.voices = voices
        
        print(f"\n📢 Available voices: {len(voices)}")
        for i, voice in enumerate(voices):
            print(f"   {i}: {voice.name}")
    
    def set_voice(self, voice_index=0):
        """Set voice by index (offline mode only)"""
        if not self.use_online and self.voices:
            self.engine.setProperty('voice', self.voices[voice_index].id)
            print(f"✅ Voice set to: {self.voices[voice_index].name}")
    
    def set_rate(self, rate=150):
        """Set speech rate (offline mode only)"""
        if not self.use_online:
            self.engine.setProperty('rate', rate)
            print(f"✅ Rate set to: {rate}")
    
    def speak(self, text, save_file=None, slow=False):
        """
        Speak the given text
        
        Args:
            text (str): Text to speak
            save_file (str): Optional filename to save audio
            slow (bool): Speak slowly (online mode only)
        """
        print(f"\n🎤 Speaking: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        if self.use_online:
            return self._speak_online(text, save_file, slow)
        else:
            return self._speak_offline(text, save_file)
    
    def _speak_online(self, text, save_file=None, slow=False):
        """Speak using gTTS (online)"""
        try:
            tts = gTTS(text=text, lang='en', slow=slow)
            
            if save_file:
                filepath = os.path.join(self.output_dir, save_file)
            else:
                filepath = os.path.join(self.output_dir, "temp_english.mp3")
            
            tts.save(filepath)
            print(f"💾 Saved: {filepath}")
            
            # Play audio
            os.system(f'start {filepath}')
            
            return filepath
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Tip: Make sure you have internet connection")
            return None
    
    def _speak_offline(self, text, save_file=None):
        """Speak using pyttsx3 (offline)"""
        try:
            if save_file:
                filepath = os.path.join(self.output_dir, save_file)
                self.engine.save_to_file(text, filepath)
                self.engine.runAndWait()
                print(f"💾 Saved: {filepath}")
                os.system(f'start {filepath}')
                return filepath
            else:
                self.engine.say(text)
                self.engine.runAndWait()
                return True
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def read_file(self, filepath, save_audio=None):
        """Read text from a file and speak it"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            
            print(f"📄 Reading file: {filepath}")
            return self.speak(text, save_audio)
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None
    
    def read_paragraph(self, text, pause_between_sentences=True):
        """Read a paragraph with natural pauses"""
        import re
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        print(f"\n📖 Reading {len(sentences)} sentences...")
        
        for i, sentence in enumerate(sentences, 1):
            print(f"\n   [{i}/{len(sentences)}] {sentence}")
            self.speak(sentence + ".")
            
            if pause_between_sentences and not self.use_online:
                import time
                time.sleep(0.5)
        
        print("\n✅ Finished reading!")


def demo_english_tts():
    """Demo function showing English TTS capabilities"""
    print("\n" + "=" * 70)
    print("🎬 English TTS Demo")
    print("=" * 70)
    
    # Online mode demo
    print("\n1️⃣ Online Mode (gTTS) - Best Quality")
    print("-" * 40)
    
    tts_online = EnglishTTS(use_online=True)
    
    examples = [
        "Hello! Welcome to the English text to speech system.",
        "This is a demonstration of natural English voice synthesis.",
        "You can use this for reading books, articles, or any text.",
        "The voice quality is clear and easy to understand.",
        "Thank you for trying our text to speech system!"
    ]
    
    for i, text in enumerate(examples, 1):
        print(f"\n📝 Example {i}:")
        tts_online.speak(text, f"english_demo_{i}.mp3")
        
        # Wait for playback
        import time
        time.sleep(3)
    
    print("\n" + "=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)


def interactive_mode():
    """Interactive English TTS"""
    print("\n" + "=" * 70)
    print("🎤 Interactive English TTS")
    print("=" * 70)
    
    print("\nChoose mode:")
    print("  1. Online (gTTS) - Better quality, needs internet")
    print("  2. Offline (pyttsx3) - Works without internet")
    
    choice = input("\nEnter choice (1/2): ").strip()
    
    use_online = choice != '2'
    tts = EnglishTTS(use_online=use_online)
    
    if not use_online:
        print("\nChoose voice:")
        for i, voice in enumerate(tts.voices):
            print(f"  {i}: {voice.name}")
        voice_choice = input("\nEnter voice number: ").strip()
        try:
            tts.set_voice(int(voice_choice))
        except:
            pass
    
    print("\n" + "-" * 40)
    print("Type text to speak (or 'quit' to exit)")
    print("-" * 40)
    
    while True:
        text = input("\n➤ ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if text:
            save = input("Save to file? (y/n): ").strip().lower()
            if save == 'y':
                filename = input("Filename (e.g. output.mp3): ").strip()
                if not filename:
                    filename = "speech.mp3"
                tts.speak(text, filename)
            else:
                tts.speak(text)


# Quick functions for easy use
def say(text, save_file=None):
    """Quick function to speak English text"""
    tts = EnglishTTS(use_online=True)
    return tts.speak(text, save_file)


def say_offline(text, save_file=None):
    """Quick function to speak English text offline"""
    tts = EnglishTTS(use_online=False)
    return tts.speak(text, save_file)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎤 English Text-to-Speech System")
    print("=" * 70)
    
    print("\nOptions:")
    print("  1. Quick demo")
    print("  2. Interactive mode")
    print("  3. Test online (gTTS)")
    print("  4. Test offline (pyttsx3)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        demo_english_tts()
    elif choice == '2':
        interactive_mode()
    elif choice == '3':
        say("Hello! This is a test of the online English text to speech system.", "test_online.mp3")
    elif choice == '4':
        say_offline("Hello! This is a test of the offline English text to speech system.", "test_offline.wav")
    else:
        # Default: simple test
        say("Welcome to English text to speech!")
