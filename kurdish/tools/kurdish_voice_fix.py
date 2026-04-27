"""
چارەسەری تایبەت بۆ دەنگی کوردی
Special solution for Kurdish voice
"""

from gtts import gTTS
import os

def speak_kurdish(text, save_path="output/kurdish_voice.mp3"):
    """
    دەنگدانەوەی دەقی کوردی
    Speak Kurdish text
    """
    print(f"🎤 دەنگدانەوەی: {text}")
    
    # هەوڵدان بۆ زمانەکانی جیاجیا
    languages_to_try = [
        ('ar', 'عەرەبی / Arabic'),
        ('fa', 'فارسی / Persian'),
        ('tr', 'تورکی / Turkish')
    ]
    
    for lang_code, lang_name in languages_to_try:
        try:
            print(f"\n   تاقیکردنەوە بە {lang_name}...")
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(save_path)
            print(f"   ✅ سەرکەوتوو! فایل پاشەکەوت کرا: {save_path}")
            
            # لێدانی دەنگ
            print(f"   ▶️ لێدان...")
            os.system(f'start {save_path}')
            return True
            
        except Exception as e:
            print(f"   ❌ سەرکەوتوو نەبوو: {e}")
            continue
    
    print("\n❌ هیچ زمانێک کار نەکرد")
    return False

# تاقیکردنەوە
if __name__ == "__main__":
    print("=" * 60)
    print("🎤 سیستەمی دەنگی کوردی")
    print("🎤 Kurdish Voice System")
    print("=" * 60)
    
    # نموونەکانی دەق
    texts = [
        "سڵاو",
        "چۆنی",
        "بەیانی باش",
        "خواحافیز"
    ]
    
    for i, text in enumerate(texts, 1):
        print(f"\n\n{'='*60}")
        print(f"نموونەی {i} / Example {i}")
        print(f"{'='*60}")
        speak_kurdish(text, f"output/kurdish_{i}.mp3")
        
        input("\nEnter بگرە بۆ بەردەوامبوون...")
    
    print("\n\n✅ هەموو نموونەکان تەواو بوون!")
