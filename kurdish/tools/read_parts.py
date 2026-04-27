from gtts import gTTS
import os
import time

print("🎤 پارچە پارچە خوێندنەوەی چیرۆک...")
print("=" * 50)

# پارچەکانی چیرۆک بە کوردی
parts_kurdish = [
    "لە گوندێکی بچووک لە کوردستان، کوڕێک هەبوو بە ناوی ئارمانج",
    "ئارمانج گەنجێکی مەهربان بوو، بەڵام دەترسا لە تاریکی",
    "دایکی پێی گوت: تاریکی ترسناک نییە، تۆ ترسی دەهێنیت",
    "ئارمانج فێربوو بڵێ: من دڵ قەویەم، من ڕووناکم",
    "لە کۆتاییدا، ئارمانج زاڵ بوو لەسەر ترسەکەی"
]

for i, text in enumerate(parts_kurdish, 1):
    print(f"\n📖 پارچەی {i}:")
    print(f"   {text}")
    
    # دروستکردنی دەنگ
    tts = gTTS(text=text, lang='ar', slow=True)
    filename = f'output/part{i}_kurdish.mp3'
    tts.save(filename)
    
    # لێدانی دەنگ
    os.system(f'start {filename}')
    print("   ⏸️  چاوەڕێ...")
    time.sleep(10)

print("\n✅ خوێندنەوەی کوردی تەواو بوو!")
