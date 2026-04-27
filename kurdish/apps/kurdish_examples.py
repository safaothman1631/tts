# نموونەی بەکارهێنانی سیستەمی TTS بە کوردی
# Kurdish TTS Usage Examples

from tts_pipeline import TTSPipeline

# دروستکردنی pipeline بە gTTS بۆ پشتگیری باشتری کوردی
# Initialize pipeline with gTTS for better Kurdish support
pipeline = TTSPipeline(engine_type="gtts")

# نموونەی یەکەم: قسەکردنی دەقی کوردی
# Example 1: Speak Kurdish text
print("نموونەی یەکەم: قسەکردنی دەقی کوردی")
pipeline.process_and_speak("سڵاو! چۆنی؟ خۆشحاڵم بە بینینت")

# نموونەی دووەم: پاشەکەوتکردنی دەنگ
# Example 2: Save to file
print("\nنموونەی دووەم: پاشەکەوتکردنی دەنگ")
pipeline.process_and_save(
    "ئەمە نموونەیەکی دەنگی کوردییە",
    output_filename="kurdish_example"
)

# نموونەی سێیەم: چەند دەقێک لە یەکجار
# Example 3: Batch processing
print("\nنموونەی سێیەم: پرۆسێسکردنی چەند دەقێک")
texts = [
    "یەکەم: بەیانی باش",
    "دووەم: ئێوارەتان باش",
    "سێیەم: شەوتان خۆش"
]
results = pipeline.batch_process(texts, output_prefix="kurdish_greetings")

print("\n✅ تەواو بوو!")
