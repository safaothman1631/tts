# ڕێنوێنی خێرا - پشتگیری زمانی کوردی
# Quick Guide - Kurdish Language Support

## دەستپێکردنی خێرا / Quick Start

### ١. دامەزراندن
```powershell
cd c:\Users\SAFA\tts
pip install -r requirements.txt
python -m textblob.download_corpora
```

### ٢. یەکەم تاقیکردنەوە
```powershell
python test_kurdish.py
```

## چوار ڕێگای بەکارهێنان / Four Ways to Use

### 1️⃣ هێڵی فەرمان / Command Line
```powershell
python main.py "دەقی کوردی" --engine gtts
```

### 2️⃣ ئەپی کوردی / Kurdish App
```powershell
python kurdish_app.py
```

### 3️⃣ کۆدی Python
```python
from tts_pipeline import TTSPipeline

pipeline = TTSPipeline(engine_type="gtts")
pipeline.process_and_speak("سڵاو! چۆنی؟")
```

### 4️⃣ نموونەکان / Examples
```powershell
python kurdish_examples.py
python demo_bilingual.py
```

## نموونەکانی خێرا / Quick Examples

### قسەکردن / Speak
```python
from tts_pipeline import TTSPipeline

p = TTSPipeline(engine_type="gtts")
p.process_and_speak("بەیانی باش! ڕۆژت خۆش بێت")
```

### پاشەکەوتکردن / Save
```python
p.process_and_save(
    "ئەمە دەنگێکی کوردییە",
    output_filename="my_audio"
)
```

### چەند دەقێک / Multiple
```python
texts = ["سڵاو", "چۆنی", "خواحافیز"]
results = p.batch_process(texts, output_prefix="greetings")
```

## فایلەکانی گرنگ / Important Files

📄 **test_kurdish.py** - تاقیکردنەوەی تەواو
📄 **kurdish_app.py** - ئەپی سادە بە menu
📄 **kurdish_examples.py** - نموونەکانی API
📄 **demo_bilingual.py** - بەراوردی کوردی/ئینگلیزی
📄 **README_Kurdish.md** - ڕێنوێنی تەواو
📄 **KURDISH_CHANGES.md** - زانیاری گۆڕانکارییەکان

## فایلەکانی دەرچوون / Output Files

هەموو دەنگەکان لە `output/` پاشەکەوت دەکرێن:
- `*.mp3` - فایلەکانی دەنگ
- `*_metadata.json` - زانیاری

## تێبینییەکانی گرنگ / Important Notes

⚠️ **بەکارهێنە `engine_type="gtts"`** بۆ پشتگیری باشتری کوردی
⚠️ **پێویستی بە ئینتەرنێتە** بۆ بزوێنەری gTTS
⚠️ **زمانی کوردی وەک "fa" دەناسرێتەوە** لە سیستەمەکە

## یارمەتی / Help

لە کێشەدا؟ بڕوانە:
- README_Kurdish.md - ڕێنوێنی تەواو
- KURDISH_CHANGES.md - وردەکاری تەکنیکی
- test_kurdish.py - نموونەکانی کارکردن

## نموونەی تەواو / Complete Example

```python
from tts_pipeline import TTSPipeline

# دروستکردن
pipeline = TTSPipeline(engine_type="gtts")

# ١. قسەکردن
pipeline.process_and_speak("سڵاو! بەخێربێیت")

# ٢. پاشەکەوتکردن
pipeline.process_and_save(
    "کوردستان خاکێکی جوانە",
    output_filename="kurdistan"
)

# ٣. چەند دەقێک
texts = [
    "بەیانی باش",
    "ئێوارەتان باش",
    "شەوتان خۆش"
]
pipeline.batch_process(texts, output_prefix="greetings")

print("✅ تەواو بوو!")
```

---

**زۆر سپاس بۆ بەکارهێنان! 🎉**
**Thank you for using! 🎉**
