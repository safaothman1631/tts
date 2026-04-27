# ڕێنوێنی تەواو - دەنگی کوردی 🎤
# Complete Guide - Kurdish Voice

## ⚠️ گرنگ / IMPORTANT

دەنگی کوردی بە بەکارهێنانی **دەنگی عەرەبی** لە gTTS کاردەکات.  
ئەمە باشترین چارەسەرە چونکە:
- ✅ کاردەکات بۆ نووسینی کوردی
- ✅ دەنگی ئۆنلاین بەکاردەهێنێت (Google)
- ✅ پێویستی بە دامەزراندنی زیادە نییە

## دەستپێکردنی خێرا 🚀

### ١. ئەپی سادە (پێشنیارکراو)

```powershell
python kurdish_simple_app.py
```

ئەم ئەپە:
- ✅ menu ـی کوردی هەیە
- ✅ دەتوانیت هەر دەقێک بنووسیت
- ✅ ٨ نموونەی ئامادە هەیە
- ✅ دەنگ بە ڕاستەوخۆ لێدەدات

### ٢. کۆدی ساکار

```python
from gtts import gTTS
import os

# دەقی کوردی
text = "سڵاو! چۆنی براکەم؟"

# دروستکردنی دەنگ
tts = gTTS(text=text, lang='ar', slow=False)
tts.save('output/my_voice.mp3')

# لێدانی دەنگ
os.system('start output/my_voice.mp3')
```

### ٣. لە هێڵی فەرمان

```powershell
python -c "from gtts import gTTS; import os; tts=gTTS('سڵاو', lang='ar'); tts.save('output/test.mp3'); os.system('start output/test.mp3')"
```

## نموونەکان 📚

### نموونەی ١: دەنگدانەوەی ساکار

```python
from gtts import gTTS
import os

def speak(text):
    tts = gTTS(text, lang='ar')
    tts.save('output/voice.mp3')
    os.system('start output/voice.mp3')

# بەکارهێنان
speak("سڵاو! بەخێربێیت")
speak("بەیانی باش")
speak("شەوتان خۆش")
```

### نموونەی ٢: پاشەکەوتکردنی دەنگەکان

```python
from gtts import gTTS

texts = {
    "greeting": "سڵاو! چۆنی؟",
    "morning": "بەیانی باش",
    "night": "شەوتان خۆش"
}

for name, text in texts.items():
    tts = gTTS(text, lang='ar')
    tts.save(f'output/{name}.mp3')
    print(f"✅ {name}.mp3 دروستکرا")
```

### نموونەی ٣: لیستی دەقەکان

```python
from gtts import gTTS
import os
import time

texts = [
    "سڵاو",
    "چۆنی",
    "باشم سوپاس",
    "خواحافیز"
]

for i, text in enumerate(texts, 1):
    print(f"{i}. {text}")
    tts = gTTS(text, lang='ar')
    filename = f'output/text_{i}.mp3'
    tts.save(filename)
    os.system(f'start {filename}')
    time.sleep(3)  # چاوەڕوان بۆ لێدانی دەنگ
```

## فایلەکانی بەردەست / Available Files

📄 **kurdish_simple_app.py** - ئەپی ساکار بە menu (پێشنیارکراو)  
📄 **kurdish_voice_fix.py** - تاقیکردنەوەی چەند زمانێک  
📄 **test_voice_engine.py** - تاقیکردنەوەی بزوێنەرەکان  

## چارەسەرکردنی کێشەکان 🔧

### کێشە: دەنگ نایەتەوە

**چارەسەر:**
```powershell
# تاقیکردنەوەی ساکار
python -c "from gtts import gTTS; import os; tts=gTTS('test', lang='ar'); tts.save('output/test.mp3'); os.system('start output/test.mp3')"
```

### کێشە: هەڵە لە gTTS

**چارەسەر:**
```powershell
# دووبارە دامەزراندنی gTTS
pip install --upgrade gTTS
```

### کێشە: پەیوەندی ئینتەرنێت

gTTS پێویستی بە ئینتەرنێتە چونکە API ـی Google بەکاردەهێنێت.

**چاودێری:**
```powershell
# تاقیکردنەوەی پەیوەندی
ping google.com
```

## نموونەی تەواو / Complete Example

```python
"""
ئەپێکی تەواو بۆ دەنگی کوردی
"""
from gtts import gTTS
import os

class KurdishVoice:
    def __init__(self):
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def speak(self, text, play=True):
        """دەنگدانەوەی دەق"""
        try:
            print(f"🎤 {text}")
            tts = gTTS(text=text, lang='ar', slow=False)
            filename = f"{self.output_dir}/temp_voice.mp3"
            tts.save(filename)
            
            if play:
                os.system(f'start {filename}')
            
            return filename
        except Exception as e:
            print(f"❌ هەڵە: {e}")
            return None
    
    def save(self, text, filename):
        """پاشەکەوتکردنی دەنگ"""
        tts = gTTS(text=text, lang='ar', slow=False)
        path = f"{self.output_dir}/{filename}.mp3"
        tts.save(path)
        print(f"✅ پاشەکەوت کرا: {path}")
        return path

# بەکارهێنان
voice = KurdishVoice()

# قسەکردن
voice.speak("سڵاو! بەخێربێیت بۆ سیستەمی دەنگی کوردی")

# پاشەکەوتکردن
voice.save("ئەمە نموونەیەکە", "example")
```

## تێبینییەکانی گرنگ ⚠️

1. **دەنگی عەرەبی بەکاردەهێنێت** - ئەمە تەنها چارەسەری بەردەستە
2. **پێویستی بە ئینتەرنێتە** - gTTS ئۆنلاینە
3. **لەوانەیە تەلەففوز ١٠٠٪ وەک کوردی نەبێت** - بەڵام تێدەگەیت
4. **بۆ ئەنجامی باشتر** - دەقەکان ساکار بگرە

## نموونەکانی دەق بۆ تاقیکردنەوە 🎯

```python
# سڵاوکردن
"سڵاو! چۆنی براکەم؟"
"بەیانی باش! ڕۆژت خۆش بێت"
"ئێوارەتان باش"
"شەوتان خۆش"

# گشتی
"زۆر سوپاس"
"ببورە"
"تکایە"
"خواحافیز"

# ڕستە
"کوردستان خاکێکی جوانە"
"زمانی کوردی زمانێکی دەوڵەمەندە"
"خۆشحاڵم بە ناسینت"
```

## ڕێگای خێراکان / Quick Commands

```powershell
# ١. ئەپی ساکار
python kurdish_simple_app.py

# ٢. تاقیکردنەوەی خێرا
python -c "from gtts import gTTS; import os; tts=gTTS('سڵاو', lang='ar'); tts.save('output/test.mp3'); os.system('start output/test.mp3')"

# ٣. دروستکردنی چەند دەنگێک
python -c "from gtts import gTTS; texts=['سڵاو','چۆنی','خواحافیز']; [gTTS(t,'ar').save(f'output/{i}.mp3') for i,t in enumerate(texts)]"
```

## پاڵپشتی / Support

کێشەت هەیە؟
1. بڕوانە **kurdish_simple_app.py** - ئەپی کارا
2. تاقی بکەرەوە **test_voice_engine.py**
3. پشکنە پەیوەندی ئینتەرنێت

---

**✅ ئامادەیە بۆ بەکارهێنان! / Ready to Use!**

🎉 **سەرکەوتوو بیت! / Good Luck!** 🎉
