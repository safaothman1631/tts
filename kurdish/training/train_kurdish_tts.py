"""
Kurdish TTS Model Training Setup
سیستەمی فێرکردنی مۆدێلی TTS بۆ زمانی کوردی

بەکارهێنانی: Coqui TTS (پێشتر Mozilla TTS)
تەکنەلۆژیا: Tacotron2 + WaveGrad
"""

import os
import json

class KurdishTTSTrainer:
    def __init__(self):
        self.project_name = "kurdish-tts"
        self.dataset_path = "recordings"
        
        print("=" * 70)
        print("🤖 سیستەمی فێرکردنی مۆدێلی TTS کوردی")
        print("   Kurdish TTS Model Training System")
        print("=" * 70)
    
    def check_requirements(self):
        """Check if all requirements are installed"""
        print("\n📋 پشکنینی پێداویستییەکان...")
        
        requirements = {
            'TTS': 'pip install TTS',
            'torch': 'pip install torch',
            'numpy': 'pip install numpy',
            'scipy': 'pip install scipy',
            'librosa': 'pip install librosa',
        }
        
        missing = []
        
        for package, install_cmd in requirements.items():
            try:
                __import__(package.lower())
                print(f"   ✅ {package} دامەزراوە")
            except ImportError:
                print(f"   ❌ {package} دانەمەزراوە")
                missing.append(install_cmd)
        
        if missing:
            print("\n⚠️  هەندێک پاکێج دانەمەزراون:")
            for cmd in missing:
                print(f"   {cmd}")
            return False
        
        return True
    
    def create_config(self):
        """Create training configuration file"""
        config = {
            "run_name": "kurdish_tts",
            "model": "tacotron2",
            
            # Dataset config
            "datasets": [{
                "name": "kurdish",
                "path": self.dataset_path,
                "meta_file_train": "metadata.csv",
                "meta_file_val": None
            }],
            
            # Audio config
            "audio": {
                "sample_rate": 22050,
                "win_length": 1024,
                "hop_length": 256,
                "num_mels": 80,
                "mel_fmin": 0,
                "mel_fmax": 8000
            },
            
            # Model config
            "use_phonemes": False,
            "phoneme_language": "ku",
            
            # Training config
            "batch_size": 32,
            "eval_batch_size": 16,
            "num_loader_workers": 4,
            "num_eval_loader_workers": 4,
            "run_eval": True,
            "test_delay_epochs": 10,
            
            "epochs": 1000,
            "text_cleaner": "basic_cleaners",
            "use_phonemes": False,
            
            "print_step": 25,
            "print_eval": False,
            "mixed_precision": False,
            
            "output_path": "outputs/",
            
            # Optimization
            "lr": 0.0001,
            "wd": 0.000001,
            "grad_clip": 5.0,
            
            # Checkpoint
            "save_step": 1000,
            "checkpoint": True,
            "keep_all_best": False,
            "keep_after": 10000,
            
            # Eval
            "run_eval": True,
            "test_sentences": [
                "سڵاو چۆنیت؟",
                "من دڵ قەویەم.",
                "کوردستان جوانە.",
                "من فێردەبم.",
                "دایکم مەهربانە."
            ]
        }
        
        config_path = "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Config دروستکرا: {config_path}")
        return config_path
    
    def prepare_dataset(self):
        """Prepare dataset for training"""
        print("\n📊 ئامادەکردنی Dataset...")
        
        metadata_path = f"{self.dataset_path}/metadata.csv"
        
        if not os.path.exists(metadata_path):
            print(f"❌ metadata.csv نەدۆزرایەوە لە {self.dataset_path}/")
            print("   تکایە یەکەم دەنگەکان تۆمار بکە!")
            return False
        
        # Count recordings
        count = 0
        with open(metadata_path, 'r', encoding='utf-8') as f:
            count = len(f.readlines())
        
        print(f"   ✅ {count} تۆمار لە dataset دا")
        
        if count < 100:
            print(f"\n⚠️  ئاگاداری: تەنها {count} تۆمارت هەیە")
            print("   پێشنیار: لانیکەم 500-1000 تۆمار بۆ مۆدێلێکی باش")
        
        return True
    
    def start_training(self):
        """Start training process"""
        print("\n🚀 دەستپێکردنی فێرکردن...")
        print("\n📝 فەرمانی فێرکردن:")
        
        cmd = """
        python -m TTS.bin.train_tacotron \\
            --config_path config.json \\
            --restore_path outputs/checkpoint_latest.pth
        """
        
        print(cmd)
        print("\n💡 بۆ دەستپێکردن، ئەم فەرمانە جێبەجێ بکە:")
        print("   python -m TTS.bin.train_tacotron --config_path config.json")
    
    def test_model(self, checkpoint_path, text):
        """Test trained model"""
        print(f"\n🧪 تاقیکردنەوەی مۆدێل...")
        print(f"   دەق: {text}")
        
        cmd = f"""
        tts --text "{text}" \\
            --model_path {checkpoint_path} \\
            --config_path config.json \\
            --out_path output_test.wav
        """
        
        print("\n💡 بۆ تاقیکردنەوە:")
        print(cmd)
    
    def create_inference_script(self):
        """Create script for using trained model"""
        script = '''"""
بەکارهێنانی مۆدێلی TTS کوردی
Using Kurdish TTS Model
"""

from TTS.api import TTS

# بارکردنی مۆدێل / Load model
tts = TTS(model_path="outputs/best_model.pth", 
          config_path="config.json")

def speak_kurdish(text, output_file="output.wav"):
    """Generate Kurdish speech"""
    print(f"🎤 {text}")
    tts.tts_to_file(text=text, file_path=output_file)
    print(f"💾 هەڵگیرا: {output_file}")
    
    # لێدان / Play
    import os
    os.system(f"start {output_file}")

# نموونەکان / Examples
if __name__ == "__main__":
    speak_kurdish("سڵاو چۆنیت براکەم؟")
    speak_kurdish("من دڵ قەویەم و من ڕووناکم.")
    speak_kurdish("کوردستان زۆر جوانە.")
'''
        
        with open("use_kurdish_tts.py", 'w', encoding='utf-8') as f:
            f.write(script)
        
        print("\n✅ سکریپتی بەکارهێنان دروستکرا: use_kurdish_tts.py")


def show_full_guide():
    """Show complete training guide"""
    guide = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║        🎓 ڕێبەری تەواوی فێرکردنی TTS کوردی                      ║
║           Complete Guide for Kurdish TTS Training                ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

1️⃣  دامەزراندنی پێداویستییەکان / Install Requirements
═══════════════════════════════════════════════════════════

   pip install TTS torch numpy scipy librosa pyaudio


2️⃣  تۆمارکردنی دەنگ / Record Voice
═══════════════════════════════════

   python voice_recorder.py
   
   - 200 ڕستە بخوێنەوە (لانیکەم)
   - پێشنیار: 500-1000 ڕستە بۆ باشترین ئەنجام
   - هەر ڕستەیەک 3-5 چرکە
   - کۆی کات: 15-30 کاتژمێر تۆمارکردن


3️⃣  ئامادەکردنی فێرکردن / Prepare Training
═══════════════════════════════════════════

   python train_kurdish_tts.py
   
   ئەمە دروستدەکات:
   - config.json → ڕێکخستنەکان
   - Dataset structure → ڕێکخستنی فایلەکان


4️⃣  دەستپێکردنی فێرکردن / Start Training
═══════════════════════════════════════════

   python -m TTS.bin.train_tacotron --config_path config.json
   
   کاتی پێویست:
   - CPU: 3-7 ڕۆژ
   - GPU (NVIDIA): 6-12 کاتژمێر
   - پێشنیار: GPU بەکاربهێنە بۆ خێرایی


5️⃣  تاقیکردنەوەی مۆدێل / Test Model
═══════════════════════════════════════

   python use_kurdish_tts.py
   
   یان:
   
   tts --text "سڵاو چۆنیت" \\
       --model_path outputs/best_model.pth \\
       --config_path config.json \\
       --out_path test.wav


6️⃣  بەکارهێنانی مۆدێل / Use Model
═══════════════════════════════════════

   from TTS.api import TTS
   
   tts = TTS(model_path="outputs/best_model.pth",
             config_path="config.json")
   
   tts.tts_to_file(text="سڵاو",
                   file_path="output.wav")


╔═══════════════════════════════════════════════════════════════════╗
║  پێداویستییە سیستەمییەکان / System Requirements                 ║
╚═══════════════════════════════════════════════════════════════════╝

✅ لانیکەم / Minimum:
   - RAM: 8 GB
   - Storage: 10 GB
   - CPU: 4 cores
   - Time: 3-7 days

⭐ پێشنیار / Recommended:
   - RAM: 16 GB+
   - Storage: 20 GB+
   - GPU: NVIDIA (4GB+ VRAM)
   - Time: 6-12 hours


╔═══════════════════════════════════════════════════════════════════╗
║  تێبینییە گرنگەکان / Important Notes                             ║
╚═══════════════════════════════════════════════════════════════════╝

⚠️  زیاتر تۆمار = مۆدێلی باشتر
    More recordings = Better model quality

⚠️  دەنگت دەبێتە دەنگی مۆدێل
    Your voice becomes the model's voice

⚠️  GPU زۆر زۆر خێراترە
    GPU is much faster than CPU

⚠️  فێرکردن کاتی زۆر دەوێت
    Training takes significant time

⚠️  باکگراوندی بێدەنگ پێویستە
    Quiet background needed for recording


╔═══════════════════════════════════════════════════════════════════╗
║  یارمەتی / Help                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

📚 Documentation: https://tts.readthedocs.io/
🐙 GitHub: https://github.com/coqui-ai/TTS
💬 Discord: https://discord.gg/5eXr5seRrv

"""
    
    print(guide)
    
    # Save guide
    with open("TRAINING_GUIDE_Kurdish.txt", 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ ڕێبەر هەڵگیرا: TRAINING_GUIDE_Kurdish.txt")


if __name__ == "__main__":
    trainer = KurdishTTSTrainer()
    
    # Check requirements
    if not trainer.check_requirements():
        print("\n⚠️  تکایە پاکێجەکان دابمەزرێنە و دووبارە هەوڵبدەوە")
    else:
        # Create config
        trainer.create_config()
        
        # Check dataset
        if trainer.prepare_dataset():
            trainer.create_inference_script()
            print("\n✅ هەموو شتێک ئامادەیە!")
            print("\nهەنگاوی داهاتوو:")
            print("   1. تۆمارکردنی دەنگ: python voice_recorder.py")
            print("   2. دەستپێکردنی فێرکردن: python -m TTS.bin.train_tacotron --config_path config.json")
        else:
            print("\n⚠️  یەکەم دەنگەکان تۆمار بکە:")
            print("   python voice_recorder.py")
    
    # Show full guide
    print("\n" + "=" * 70)
    show_full_guide()
