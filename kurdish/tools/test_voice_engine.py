"""
تاقیکردنەوەی دەنگی کوردی بە pyttsx3
Testing Kurdish audio with pyttsx3
"""

import pyttsx3

print("تاقیکردنەوەی بزوێنەری pyttsx3...")
print("Testing pyttsx3 engine...")

# دروستکردنی بزوێنەر
engine = pyttsx3.init()

# لیستی دەنگەکان
print("\nدەنگە بەردەستەکان / Available voices:")
voices = engine.getProperty('voices')
for i, voice in enumerate(voices):
    print(f"{i}. {voice.name}")

# تاقیکردنەوەی ئینگلیزی
print("\n\n1. تاقیکردنەوەی ئینگلیزی / Testing English:")
engine.say("Hello, this is a test")
engine.runAndWait()

# تاقیکردنەوەی کوردی
print("\n2. تاقیکردنەوەی کوردی / Testing Kurdish:")
kurdish_text = "سڵاو چۆنی"
print(f"   Text: {kurdish_text}")
engine.say(kurdish_text)
engine.runAndWait()

print("\n✅ تەواو بوو / Done!")
