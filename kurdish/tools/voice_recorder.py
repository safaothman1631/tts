"""
Kurdish Voice Recorder
پرۆگرامی تۆمارکردنی دەنگی کوردی بۆ فێرکردنی TTS

تایبەتمەندییەکان:
- خوێندنەوەی ڕستەکان یەک بە یەک
- تۆمارکردنی دەنگی بەکارهێنەر
- دووبارە تۆمارکردنەوە ئەگەر پێویست بوو
- هەڵگرتنی دەنگەکان بە یاسا
"""

import pyaudio
import wave
import os
from datetime import datetime

class KurdishVoiceRecorder:
    def __init__(self, dataset_file="kurdish_dataset.txt", output_dir="recordings"):
        self.dataset_file = dataset_file
        self.output_dir = output_dir
        self.sentences = []
        self.current_index = 0
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 22050  # Standard for TTS training
        
        # Create output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Load sentences
        self.load_sentences()
        
        print("=" * 70)
        print("🎙️  پرۆگرامی تۆمارکردنی دەنگی کوردی")
        print("   Kurdish Voice Recorder for TTS Training")
        print("=" * 70)
        print(f"\n📚 کۆی ڕستەکان: {len(self.sentences)}")
        print(f"💾 شوێنی هەڵگرتن: {output_dir}/")
        print("\nڕێنمایی:")
        print("  ENTER = دەستپێکردنی تۆمار")
        print("  SPACE = وەستاندنی تۆمار")
        print("  r = دووبارە تۆمارکردنەوە")
        print("  s = پەڕینەوە بۆ دواتر")
        print("  q = دەرچوون")
        print("=" * 70)
    
    def load_sentences(self):
        """Load sentences from dataset file"""
        with open(self.dataset_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    self.sentences.append(line)
        print(f"✅ {len(self.sentences)} ڕستە بارکرا")
    
    def record_audio(self, duration=5):
        """Record audio for specified duration"""
        audio = pyaudio.PyAudio()
        
        print("\n🔴 تۆمارکردن دەستپێدەکات...")
        
        stream = audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        frames = []
        
        for i in range(0, int(self.RATE / self.CHUNK * duration)):
            data = stream.read(self.CHUNK)
            frames.append(data)
        
        print("⏹️  تۆمار وەستا")
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        return frames
    
    def save_audio(self, frames, filename):
        """Save recorded audio to file"""
        audio = pyaudio.PyAudio()
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        print(f"💾 هەڵگیرا: {filename}")
    
    def start_recording(self):
        """Start the recording process"""
        while self.current_index < len(self.sentences):
            sentence = self.sentences[self.current_index]
            
            print("\n" + "=" * 70)
            print(f"📖 ڕستەی {self.current_index + 1} لە {len(self.sentences)}")
            print(f"\n   {sentence}\n")
            print("=" * 70)
            print("پێشکەشکراو بۆ تۆمارکردن (ENTER = تۆمار، s = پەڕینەوە، q = دەرچوون)")
            
            command = input("➤ ").strip().lower()
            
            if command == 'q':
                print("\n👋 تۆمارکردن کۆتایی هات")
                print(f"✅ کۆی تۆمارکراو: {self.current_index} ڕستە")
                break
            
            elif command == 's':
                print("⏭️  پەڕینەوە...")
                self.current_index += 1
                continue
            
            elif command == '' or command == 'r':
                # Record
                filename = f"{self.output_dir}/sentence_{self.current_index:04d}.wav"
                
                print("\n⏱️  ئامادەبە... تۆمار دەستپێدەکات لە 3 چرکە...")
                import time
                for i in range(3, 0, -1):
                    print(f"   {i}...")
                    time.sleep(1)
                
                frames = self.record_audio(duration=5)
                self.save_audio(frames, filename)
                
                # Ask if want to re-record
                print("\nتۆمارەکە باشە؟ (y = بەڵێ، r = دووبارە، q = دەرچوون)")
                confirm = input("➤ ").strip().lower()
                
                if confirm == 'r':
                    print("🔄 دووبارە تۆمارکردنەوە...")
                    continue
                elif confirm == 'q':
                    print("\n👋 تۆمارکردن کۆتایی هات")
                    break
                else:
                    print("✅ تۆمار قبووڵکرا")
                    self.current_index += 1
            
            else:
                print("❌ فەرمانی نادروست")
        
        # Create metadata file
        self.create_metadata()
    
    def create_metadata(self):
        """Create metadata.csv for training"""
        metadata_path = f"{self.output_dir}/metadata.csv"
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            for i in range(self.current_index):
                sentence = self.sentences[i]
                filename = f"sentence_{i:04d}.wav"
                f.write(f"{filename}|{sentence}\n")
        
        print(f"\n📄 Metadata دروستکرا: {metadata_path}")
        print("✅ ئامادەیە بۆ فێرکردنی مۆدێل!")


if __name__ == "__main__":
    try:
        recorder = KurdishVoiceRecorder()
        recorder.start_recording()
    except KeyboardInterrupt:
        print("\n\n⚠️  پرۆگرام وەستێندرا")
    except Exception as e:
        print(f"\n❌ هەڵە: {e}")
        print("\n💡 دڵنیابە لەوەی pyaudio دامەزراوە:")
        print("   pip install pyaudio")
