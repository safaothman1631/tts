"""
Quick test script for TTS system
"""
from tts_pipeline import TTSPipeline

print("🎤 Testing TTS with NLP Pipeline\n")

# Initialize
pipeline = TTSPipeline()

# Test 1: Simple text
print("=" * 60)
print("Test 1: Simple greeting")
print("=" * 60)
pipeline.process_and_speak("Hello! Welcome to the advanced text to speech system.")

# Test 2: Numbers and formatting
print("\n" + "=" * 60)
print("Test 2: Numbers and currency")
print("=" * 60)
text2 = "Dr. Smith earned $50,000 in 2023, which is a 25% increase."
pipeline.process_and_speak(text2)

# Test 3: Save to file
print("\n" + "=" * 60)
print("Test 3: Saving to audio file")
print("=" * 60)
text3 = "This audio will be saved to a file for later playback."
pipeline.process_and_save(text3, output_filename="test_output")

print("\n✅ All tests completed successfully!")
print("Check the 'output' folder for saved audio files.")
