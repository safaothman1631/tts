"""
🎤 Kurdish TTS Training System - Using Piper
سیستەمی فێرکردنی TTS کوردی - بە Piper

Piper is lightweight and works with any Python version!
"""

import os
import json
import wave
import struct

class KurdishTTSTrainer:
    def __init__(self):
        self.dataset_dir = "kurdish_dataset"
        self.recordings_dir = "recordings" 
        self.output_dir = "trained_model"
        
        # Create directories
        for d in [self.dataset_dir, self.recordings_dir, self.output_dir]:
            os.makedirs(d, exist_ok=True)
        
        print("=" * 65)
        print("🎤 سیستەمی فێرکردنی TTS کوردی")
        print("   Kurdish TTS Training System")
        print("=" * 65)
    
    def show_options(self):
        """Show training options"""
        print("""
╔═══════════════════════════════════════════════════════════════╗
║  ڕێگاکانی دروستکردنی TTS کوردی                               ║
╚═══════════════════════════════════════════════════════════════╝

🅰️  ڕێگای ئاسان: Voice Cloning (پێشنیار!)
   ────────────────────────────────────────
   ✅ تەنها 1-5 دەقیقە دەنگ پێویستە
   ✅ زۆر خێرایە (چەند دەقیقە)
   ✅ کوالیتی باش
   
   ئامرازەکان:
   • Coqui XTTS (Python 3.10-3.11)
   • ElevenLabs (ئۆنلاین)
   • PlayHT (ئۆنلاین)
   

🅱️  ڕێگای تەواو: Full Training
   ────────────────────────────────────────
   ⚠️  500-1000 تۆمار پێویستە
   ⚠️  چەندین ڕۆژ کات دەوێت
   ⚠️  GPU پێویستە
   
   ئامرازەکان:
   • Piper TTS
   • Coqui TTS
   • StyleTTS2


🅲️  ڕێگای ناوەندی: Fine-tuning
   ────────────────────────────────────────
   ✅ 50-100 تۆمار پێویستە
   ✅ 2-4 کاتژمێر
   ✅ کوالیتی باش
   
   ئامرازەکان:
   • Piper (fine-tune)
   • XTTS (fine-tune)
""")
    
    def setup_voice_cloning(self):
        """Setup voice cloning - easiest method"""
        print("""
╔═══════════════════════════════════════════════════════════════╗
║  🅰️  Voice Cloning - ڕێگای ئاسان                              ║
╚═══════════════════════════════════════════════════════════════╝

ئەم ڕێگایە تەنها پێویستی بە 1-5 دەقیقە دەنگ هەیە!

═══════════════════════════════════════════════════════════════

📋 هەنگاوەکان:

1️⃣  دەنگت تۆمار بکە (1-5 دەقیقە)
    ─────────────────────────────────
    • چەند ڕستەیەکی کوردی بخوێنەوە
    • دەنگ ڕوون و بێدەنگ بێت
    • بە mp3 یان wav هەڵیبگرە
    

2️⃣  ئەپێکی Voice Cloning بەکاربهێنە
    ─────────────────────────────────
    
    🌐 ئۆنلاین (بێ دامەزراندن):
    
    • ElevenLabs.io
      - سەردان بکە: https://elevenlabs.io
      - دەنگەکەت ئەپلۆد بکە
      - ئینجا دەقی کوردی بنووسە
      - AI بە دەنگی تۆ دەیخوێنێتەوە!
    
    • PlayHT.com  
      - سەردان بکە: https://play.ht
      - Voice Cloning بکە
      - زۆر ئاسانە!
    
    
    💻 ئۆفلاین (لەسەر کۆمپیوتەری خۆت):
    
    • Coqui XTTS
      - پێویستی بە Python 3.10-3.11 هەیە
      - دامەزرێنە: pip install coqui-tts
      - تاقیبکەرەوە


═══════════════════════════════════════════════════════════════

🎙️ با دەنگت تۆمار بکەین!

ئەم ڕستانە بخوێنەوە و تۆماری بکە:
""")
        
        sentences = [
            "سڵاو! ناوی من ئارمانجە و من لە کوردستان دەژیم.",
            "ئەمڕۆ ڕۆژێکی زۆر جوانە و خۆر دەدرەوشێتەوە.",
            "من زۆر خۆشحاڵم کە تۆ لێرەیت و باسی لەگەڵ دەکەم.",
            "کوردستان وڵاتێکی جوانە و خەڵکەکەی مەهربانن.",
            "فێربوون شتێکی باشە و هەموو کەس دەبێت فێربێت.",
            "دایکم و باوکم زۆر خۆشمدەوێن و من خۆشمدەوێن.",
            "من حەزدەکەم کتێب بخوێنمەوە و شتی نوێ فێربم.",
            "هیوادارم کە ئەم ڕۆژە ڕۆژێکی باش بێت بۆ هەموومان.",
        ]
        
        print("📝 ئەم ڕستانە یەک بە یەک بخوێنەوە:\n")
        for i, s in enumerate(sentences, 1):
            print(f"   {i}. {s}\n")
        
        print("""
═══════════════════════════════════════════════════════════════

📱 چۆن تۆمار بکەم?

   • Windows: Voice Recorder app
   • Phone: هەر ئەپێکی تۆمارکردن
   • Online: vocaroo.com

   هەڵیبگرە وەک: my_voice.mp3 یان my_voice.wav


═══════════════════════════════════════════════════════════════

🌐 پاشان سەردانی ئەم سایتانە بکە:

   1. https://elevenlabs.io (باشترینە)
   2. https://play.ht
   3. https://resemble.ai

   دەنگەکەت ئەپلۆد بکە، ئینجا دەقی کوردی بنووسە!
""")


def record_voice_sample():
    """Record a voice sample for cloning"""
    import pyaudio
    import wave
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🎙️  تۆمارکردنی دەنگ بۆ Voice Cloning                        ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    sentences = [
        "سڵاو! ناوی من ئارمانجە و من لە کوردستان دەژیم.",
        "ئەمڕۆ ڕۆژێکی زۆر جوانە و خۆر دەدرەوشێتەوە.",
        "من زۆر خۆشحاڵم کە تۆ لێرەیت.",
        "کوردستان وڵاتێکی جوانە.",
        "فێربوون شتێکی باشە.",
    ]
    
    print("📝 ئەم ڕستانە دەخوێنیتەوە:\n")
    for i, s in enumerate(sentences, 1):
        print(f"   {i}. {s}")
    
    print("\n" + "=" * 60)
    input("\n⏎ کلیک بکە لەسەر ENTER بۆ دەستپێکردنی تۆمار...")
    
    # Audio settings
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 22050
    RECORD_SECONDS = 60  # 1 minute max
    
    audio = pyaudio.PyAudio()
    
    print("\n🔴 تۆمارکردن دەستپێکرد! (60 چرکە)")
    print("   ڕستەکان بخوێنەوە...")
    print("   CTRL+C بۆ وەستان\n")
    
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    frames = []
    
    try:
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
            
            # Show progress
            seconds = i * CHUNK / RATE
            if int(seconds) % 10 == 0 and int(seconds) > 0:
                print(f"   ⏱️  {int(seconds)} چرکە...")
                
    except KeyboardInterrupt:
        print("\n⏹️  تۆمار وەستا")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save
    filename = "my_voice_sample.wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    print(f"\n✅ تۆمار هەڵگیرا: {filename}")
    print(f"   درێژایی: {len(frames) * CHUNK / RATE:.1f} چرکە")
    print("""
═══════════════════════════════════════════════════════════════

🎯 هەنگاوی داهاتوو:

   1. فایلی {0} ئەپلۆد بکە بۆ:
      • https://elevenlabs.io
      • https://play.ht
   
   2. Voice Cloning بکە
   
   3. دەقی کوردی بنووسە و گوێ بگرە!

═══════════════════════════════════════════════════════════════
""".format(filename))


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    🎤 سیستەمی دروستکردنی TTS کوردی                           ║
║       Kurdish TTS Creation System                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

ڕێگاکان:

   1️⃣  Voice Cloning (ئاسان - پێشنیار!) ⭐
       تەنها 1-5 دەقیقە دەنگ پێویستە
   
   2️⃣  تۆمارکردنی دەنگ
       دەنگت تۆمار دەکات بۆ Voice Cloning
   
   3️⃣  ڕێنمایی تەواو
       هەموو ڕێگاکان ڕوون دەکاتەوە

""")
    
    choice = input("هەڵبژاردن (1-3): ").strip()
    
    trainer = KurdishTTSTrainer()
    
    if choice == '1':
        trainer.setup_voice_cloning()
    elif choice == '2':
        record_voice_sample()
    elif choice == '3':
        trainer.show_options()
    else:
        trainer.setup_voice_cloning()


if __name__ == "__main__":
    main()
