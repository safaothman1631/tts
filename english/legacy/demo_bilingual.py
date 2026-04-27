"""
Demo: Kurdish and English TTS Comparison
نیشاندان: بەراوردکردنی TTS بە کوردی و ئینگلیزی
"""

from tts_pipeline import TTSPipeline
import time

print("=" * 70)
print("🎤 TTS System - Kurdish & English Demo")
print("🎤 سیستەمی TTS - نمایشی کوردی و ئینگلیزی")
print("=" * 70)

# Initialize with gTTS for better language support
pipeline = TTSPipeline(engine_type="gtts")

# Demo 1: Greetings in both languages
print("\n📢 Demo 1: Greetings / سڵاوکردن")
print("-" * 70)

print("\n🇬🇧 English:")
pipeline.process_and_speak("Hello! Welcome to the text to speech system.")

time.sleep(1)

print("\n🇮🇶 Kurdish / کوردی:")
pipeline.process_and_speak("سڵاو! بەخێربێیت بۆ سیستەمی گۆڕینی نووسین بۆ دەنگ")

# Demo 2: Save files in both languages
print("\n\n📢 Demo 2: Saving Audio Files / پاشەکەوتکردنی فایلی دەنگ")
print("-" * 70)

print("\n🇬🇧 Saving English audio...")
pipeline.process_and_save(
    "This is an English text-to-speech example.",
    output_filename="demo_english"
)

print("\n🇮🇶 پاشەکەوتکردنی دەنگی کوردی...")
pipeline.process_and_save(
    "ئەمە نموونەیەکی گۆڕینی نووسین بۆ دەنگە بە کوردی",
    output_filename="demo_kurdish"
)

# Demo 3: Mixed content with numbers
print("\n\n📢 Demo 3: Numbers and Dates / ژمارە و بەروار")
print("-" * 70)

print("\n🇬🇧 English with numbers:")
pipeline.process_and_speak("The meeting is scheduled for 2024 at 3 PM.")

time.sleep(1)

print("\n🇮🇶 کوردی لەگەڵ ژمارە:")
pipeline.process_and_speak("کۆبوونەوەکە لە ساڵی 2024 دایندەنرێت")

# Final summary
print("\n\n✅ Demo completed! / تەواو بوو!")
print("=" * 70)
print("📁 Audio files saved in 'output' folder")
print("📁 فایلە دەنگییەکان لە بوخچەی 'output' پاشەکەوت کران")
print("\nFiles created:")
print("  - demo_english.mp3")
print("  - demo_kurdish.mp3")
print("=" * 70)
