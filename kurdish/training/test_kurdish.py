"""
تاقیکردنەوەی سیستەمی TTS بۆ زمانی کوردی
Kurdish Language TTS Testing
"""
from tts_pipeline import TTSPipeline

print("🎤 تاقیکردنەوەی سیستەمی گۆڕینی نووسین بۆ دەنگ بە کوردی")
print("🎤 Testing Kurdish Text-to-Speech System")
print("=" * 60)

# Initialize pipeline with gTTS for better Kurdish support
pipeline = TTSPipeline(engine_type="gtts")

# Test 1: Simple Kurdish greeting
print("\nتاقیکردنەوەی یەکەم: سڵاوکردنی ساکار")
print("Test 1: Simple greeting")
print("-" * 60)
text1 = "سڵاو! بەخێربێیت بۆ سیستەمی گۆڕینی نووسین بۆ دەنگ"
print(f"دەق: {text1}")
pipeline.process_and_speak(text1)

# Test 2: Kurdish text with numbers
print("\n\nتاقیکردنەوەی دووەم: ژمارە بە کوردی")
print("Test 2: Numbers in Kurdish")
print("-" * 60)
text2 = "ژمارەی 1 و 2 و 3 و 10 بە کوردی"
print(f"دەق: {text2}")
pipeline.process_and_speak(text2)

# Test 3: Save Kurdish audio
print("\n\nتاقیکردنەوەی سێیەم: هەڵگرتنی دەنگ")
print("Test 3: Save to audio file")
print("-" * 60)
text3 = "ئەم دەنگە بە کوردی دەپارێزرێت بۆ گوێگرتنی دواتر"
print(f"دەق: {text3}")
pipeline.process_and_save(text3, output_filename="kurdish_test")

# Test 4: Mixed content
print("\n\nتاقیکردنەوەی چوارەم: ناوەڕۆکی تێکەڵ")
print("Test 4: Mixed content")
print("-" * 60)
text4 = "د. ئەحمەد لە ساڵی 2023 کارەکەی دەست پێکرد"
print(f"دەق: {text4}")
pipeline.process_and_speak(text4)

# Test 5: Longer Kurdish text
print("\n\nتاقیکردنەوەی پێنجەم: دەقی درێژ")
print("Test 5: Longer text")
print("-" * 60)
text5 = """
کوردستان خاکێکی جوانە لە باکووری عێراق. 
خەڵکی کوردستان بە میواننوازی و دڵسۆزییان ناسراون.
زمانی کوردی زمانێکی کۆنە و دەوڵەمەندە.
"""
print(f"دەق: {text5}")
pipeline.process_and_save(text5, output_filename="kurdish_long_text")

print("\n\n✅ هەموو تاقیکردنەوەکان بە سەرکەوتوویی تەواو بوون!")
print("✅ All tests completed successfully!")
print("📁 فایلەکان لە بوخچەی 'output' پاشەکەوت کراون")
print("📁 Files saved in 'output' folder")
