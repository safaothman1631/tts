# چۆن دەنگی کوردی بەکاربهێنم؟ 🎤
# How to Use Kurdish Voice?

## کێشەکە چی بوو؟ / What was the problem?

سیستەمی سەرەتا هەوڵی دەدا دەنگی کوردی دروست بکات بە گۆڕینی نووسینی کوردی بۆ دەنگی عەرەبی لە gTTS. **بەڵام gTTS پێویستی بە ئینتەرنێتە** و لە کاتی تاقیکردنەوە پەیوەندی ئینتەرنێت نەبوو.

## چارەسەرەکان / Solutions

### چارەسەری ١: بە ئینتەرنێت (gTTS) - باشترینە ✅

```python
from gtts import gTTS
import os

# دەقی کوردی
text = "سڵاو چۆنی براکەم"

# دروستکردنی دەنگ بە عەرەبی
tts = gTTS(text=text, lang='ar', slow=False)
tts.save('output/voice.mp3')

# لێدانی دەنگ
os.system('start output/voice.mp3')
```

**پێویستە:**
- ✅ پەیوەندی ئینتەرنێت
- ✅ gTTS دامەزراو بێت
- ✅ دەنگی باش و سروشتی

**بەکارهێنان:**
```powershell
python kurdish_simple_app.py
```

### چارەسەری ٢: بێ ئینتەرنێت (pyttsx3) - ئۆفلاین ⚡

```python
import pyttsx3

# دروستکردنی بزوێنەر
engine = pyttsx3.init()

# دەقی کوردی بە لاتینی
text = "sallaw chonee"  # سڵاو چۆنی

# قسەکردن
engine.say(text)
engine.runAndWait()
```

**پێویستە:**
- ✅ پێویستی بە ئینتەرنێت نییە
- ✅ pyttsx3 دامەزراو بێت
- ❌ دەنگ وەک کوردی نییە (دەنگی ئینگلیزییە)
- ❌ پێویستە دەق بە لاتینی بنووسیت

**بەکارهێنان:**
```powershell
python kurdish_offline_app.py
```

## بەراوردکردن / Comparison

| تایبەتمەندی | gTTS (ئۆنلاین) | pyttsx3 (ئۆفلاین) |
|-------------|----------------|-------------------|
| ئینتەرنێت | پێویستە ✅ | پێویست نییە ❌ |
| نووسینی کوردی | کاردەکات ✅ | کار ناکات ❌ |
| دەنگی سروشتی | باش ✅ | لاواز ❌ |
| خێرایی | هێواش (ئۆنلاین) | خێرا ⚡ |
| پێشنیار | **باشترینە** 🌟 | بۆ تاقیکردنەوە |

## ڕێگای پێشنیارکراو / Recommended Way

### ١. پشکنینی ئینتەرنێت

```powershell
# تاقیکردنەوەی پەیوەندی
ping google.com
```

### ٢. ئەگەر ئینتەرنێت هەبوو

```powershell
# بەکارهێنانی ئەپی ئۆنلاین (باشترینە)
python kurdish_simple_app.py
```

**یان کۆدی ساکار:**

```python
from gtts import gTTS
import os

def speak_kurdish(text):
    """دەنگدانەوەی کوردی بە دەنگی عەرەبی"""
    print(f"🎤 {text}")
    tts = gTTS(text=text, lang='ar')
    tts.save('output/voice.mp3')
    os.system('start output/voice.mp3')

# بەکارهێنان
speak_kurdish("سڵاو! چۆنی براکەم؟")
speak_kurdish("بەیانی باش")
speak_kurdish("شەوتان خۆش")
```

### ٣. ئەگەر ئینتەرنێت نەبوو

```powershell
# بەکارهێنانی ئەپی ئۆفلاین
python kurdish_offline_app.py
```

**یان کۆدی ساکار:**

```python
import pyttsx3

engine = pyttsx3.init()

# دەق بە لاتینی بنووسە
texts = [
    "sallaw",           # سڵاو
    "bayanee bash",     # بەیانی باش
    "shawtan khosh",    # شەوتان خۆش
]

for text in texts:
    print(f"🎤 {text}")
    engine.say(text)
    engine.runAndWait()
```

## نموونەکانی تەواو / Complete Examples

### نموونەی ١: دروستکردنی چەند دەنگێک (ئۆنلاین)

```python
from gtts import gTTS
import os

# دەقەکانی کوردی
kurdish_texts = {
    "greeting": "سڵاو! چۆنی؟",
    "morning": "بەیانی باش! ڕۆژت خۆش بێت",
    "evening": "ئێوارەتان باش",
    "night": "شەوتان خۆش",
    "thanks": "زۆر سوپاس",
    "sorry": "ببورە",
    "goodbye": "خواحافیز! خوات لەگەڵ بێت"
}

print("دروستکردنی فایلەکانی دەنگ...")
for name, text in kurdish_texts.items():
    print(f"  {name}: {text}")
    tts = gTTS(text=text, lang='ar')
    tts.save(f'output/{name}_kurdish.mp3')
    print(f"    ✅ {name}_kurdish.mp3")

print("\n✅ هەموو فایلەکان دروستکران!")
print("📁 بڕوانە بوخچەی: output/")
```

### نموونەی ٢: کلاسێکی تەواو

```python
from gtts import gTTS
import os
import time

class KurdishVoice:
    """
    کلاسی دەنگی کوردی
    """
    
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def speak(self, text, play=True):
        """قسەکردنی دەقی کوردی"""
        try:
            print(f"🎤 {text}")
            tts = gTTS(text=text, lang='ar', slow=False)
            temp_file = f"{self.output_dir}/temp.mp3"
            tts.save(temp_file)
            
            if play:
                os.system(f'start {temp_file}')
                time.sleep(2)
            
            return temp_file
        except Exception as e:
            print(f"❌ هەڵە: {e}")
            return None
    
    def save(self, text, filename):
        """پاشەکەوتکردنی دەنگ"""
        try:
            filepath = f"{self.output_dir}/{filename}.mp3"
            tts = gTTS(text=text, lang='ar', slow=False)
            tts.save(filepath)
            print(f"✅ پاشەکەوت کرا: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ هەڵە: {e}")
            return None
    
    def batch_speak(self, texts, delay=2):
        """قسەکردنی چەند دەقێک"""
        for i, text in enumerate(texts, 1):
            print(f"\n[{i}/{len(texts)}]")
            self.speak(text)
            if i < len(texts):
                time.sleep(delay)

# بەکارهێنان
voice = KurdishVoice()

# نموونەی ١
voice.speak("سڵاو! بەخێربێیت")

# نموونەی ٢
voice.save("کوردستان خاکێکی جوانە", "kurdistan")

# نموونەی ٣
greetings = [
    "سڵاو",
    "چۆنی",
    "باشم سوپاس",
    "خواحافیز"
]
voice.batch_speak(greetings)
```

## تێبینییەکانی گرنگ ⚠️

### ١. دەربارەی gTTS (ئۆنلاین)

- ✅ **باشترین چارەسەرە** بۆ کوردی
- ✅ دەنگی سروشتی و باش
- ✅ نووسینی کوردی ڕاستەوخۆ بەکاردەهێنێت
- ❌ پێویستی بە ئینتەرنێتە
- ❌ لەوانەیە هێواش بێت

### ٢. دەربارەی pyttsx3 (ئۆفلاین)

- ✅ پێویستی بە ئینتەرنێت نییە
- ✅ زۆر خێراە
- ❌ **ناتوانێت نووسینی کوردی بخوێنێتەوە**
- ❌ دەنگ وەک ئینگلیزی دەبێت
- ❌ پێویستە دەق بە لاتینی بنووسیت

### ٣. چۆن دەقی کوردی بنووسم بۆ pyttsx3؟

| کوردی | لاتینی (بۆ pyttsx3) |
|-------|---------------------|
| سڵاو | sallaw |
| چۆنی | chonee |
| بەیانی باش | bayanee bash |
| شەوتان خۆش | shawtan khosh |
| زۆر سوپاس | zor supas |
| ببورە | bboora |
| خواحافیز | khwa hafiz |

## فایلەکانی بەردەست / Available Files

📄 **kurdish_simple_app.py** - ئەپی ئۆنلاین (پێشنیارکراو) ⭐  
📄 **kurdish_offline_app.py** - ئەپی ئۆفلاین  
📄 **kurdish_voice_fix.py** - تاقیکردنەوەی چەند زمانێک  
📄 **test_voice_engine.py** - تاقیکردنەوەی بزوێنەرەکان  
📄 **KURDISH_VOICE_GUIDE.md** - ڕێنوێنی تەواو  

## تاقیکردنەوەی خێرا / Quick Test

### بە ئینتەرنێت:
```powershell
python -c "from gtts import gTTS; import os; tts=gTTS('سڵاو','ar'); tts.save('test.mp3'); os.system('start test.mp3')"
```

### بێ ئینتەرنێت:
```powershell
python -c "import pyttsx3; e=pyttsx3.init(); e.say('sallaw'); e.runAndWait()"
```

## یارمەتی / Help

کێشەت هەیە؟

1. **ئینتەرنێت نییە؟**
   - بەکاربهێنە `kurdish_offline_app.py`
   - دەق بە لاتینی بنووسە

2. **دەنگ نایەتەوە؟**
   - بپشکنە قەبارەی سیستەم
   - بپشکنە ئامێرەکانی دەنگ

3. **هەڵە لە gTTS؟**
   - بپشکنە پەیوەندی ئینتەرنێت
   - دووبارە بەکاری بهێنەوە

---

## کورتە / Summary

✅ **ئەگەر ئینتەرنێتت هەیە**: بەکاربهێنە `kurdish_simple_app.py` (باشترینە)  
✅ **ئەگەر ئینتەرنێتت نییە**: بەکاربهێنە `kurdish_offline_app.py` (دەق بە لاتینی)  

🎉 **سەرکەوتوو بیت! / Good Luck!** 🎉
