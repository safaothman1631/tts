import pyttsx3
import time

print("🎤 خوێندنەوە بە ئینگلیزی (لاتینی)...")
print("=" * 50)

# دروستکردنی بزوێنەر
engine = pyttsx3.init()
engine.setProperty('rate', 130)  # هێواشتر
engine.setProperty('volume', 1.0)

# پارچەکانی چیرۆک بە لاتینی
parts_latin = [
    "La gondeki bchook la Kurdestan, korek habu ba nawi Armanj",
    "Armanj genjeki mahraban bu, ballam datrsa la tarikee",
    "Daykee pay gwut: tarikee tarsnnak neya, to trasee dahenet",
    "Armanj ferbu blle: man dall qaweyam, man roonakam",
    "La kotayeeda, Armanj zall bu lasar trasaka-ee"
]

for i, text in enumerate(parts_latin, 1):
    print(f"\n📖 پارچەی {i}:")
    print(f"   {text}")
    print("   🔊 لێدان...")
    
    engine.say(text)
    engine.runAndWait()
    
    print("   ⏸️  چاوەڕێ...")
    time.sleep(2)

print("\n✅ خوێندنەوەی ئینگلیزی تەواو بوو!")
