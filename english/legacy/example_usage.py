"""
Example usage of the TTS Pipeline with various features
"""

from tts_pipeline import TTSPipeline


def example_basic_usage():
    """Basic text-to-speech conversion"""
    print("\n" + "="*60)
    print("Example 1: Basic Usage")
    print("="*60)
    
    pipeline = TTSPipeline()
    text = "Hello, this is a simple text to speech example."
    
    # Process and speak
    pipeline.process_and_speak(text)


def example_with_numbers():
    """Text with numbers and special formatting"""
    print("\n" + "="*60)
    print("Example 2: Numbers and Special Formatting")
    print("="*60)
    
    pipeline = TTSPipeline()
    text = """
    Dr. Johnson earned $50,000 in 2023, which represents a 15% increase 
    from 2022. He finished 1st in his department, beating the 2nd place 
    by a significant margin.
    """
    
    # Process and save to file
    pipeline.process_and_save(text, output_filename="numbers_example")


def example_emotion_detection():
    """Text with different emotions"""
    print("\n" + "="*60)
    print("Example 3: Emotion Detection")
    print("="*60)
    
    pipeline = TTSPipeline()
    
    # Happy text
    happy_text = "I'm so excited and thrilled! This is absolutely wonderful news!"
    print("\n😊 Happy text:")
    pipeline.process_and_speak(happy_text)
    
    # Sad text
    sad_text = "I feel terrible and disappointed. Everything seems so hopeless."
    print("\n😢 Sad text:")
    pipeline.process_and_speak(sad_text)
    
    # Neutral text
    neutral_text = "The meeting is scheduled for tomorrow at 3 PM in conference room B."
    print("\n😐 Neutral text:")
    pipeline.process_and_speak(neutral_text)


def example_batch_processing():
    """Batch process multiple texts"""
    print("\n" + "="*60)
    print("Example 4: Batch Processing")
    print("="*60)
    
    pipeline = TTSPipeline()
    
    texts = [
        "First announcement: All staff meeting at 10 AM.",
        "Second announcement: Lunch will be provided.",
        "Third announcement: Please bring your laptops."
    ]
    
    results = pipeline.batch_process(texts, output_prefix="announcement")
    
    print("\n📊 Batch Processing Results:")
    for result in results:
        if result['success']:
            print(f"✅ Text {result['index']}: Success")
        else:
            print(f"❌ Text {result['index']}: Failed - {result['error']}")


def example_multi_language():
    """Multi-language text processing"""
    print("\n" + "="*60)
    print("Example 5: Multi-language Detection")
    print("="*60)
    
    pipeline = TTSPipeline()
    
    texts = [
        "This is an English sentence.",
        "Ceci est une phrase française.",
        "Dies ist ein deutscher Satz.",
    ]
    
    for text in texts:
        print(f"\n🌍 Processing: {text}")
        processed, metadata = pipeline.nlp_processor.process_text(text)
        print(f"   Detected language: {metadata['language']}")


def example_complex_text():
    """Complex text with various NLP features"""
    print("\n" + "="*60)
    print("Example 6: Complex Text Processing")
    print("="*60)
    
    pipeline = TTSPipeline()
    
    text = """
    Apple Inc. announced on January 15th, 2024 that its Q4 revenue reached 
    $125.5 billion, marking a 12.3% year-over-year increase. CEO Tim Cook 
    stated, "We're thrilled with these results." The stock price rose to 
    $185.50, up $7.25 or 4.1% from the previous close. Analysts at 
    Morgan Stanley rated it as a strong buy, with a target price of $200.
    """
    
    pipeline.process_and_save(text, output_filename="complex_example")


def example_custom_voice_settings():
    """Custom voice configuration"""
    print("\n" + "="*60)
    print("Example 7: Custom Voice Settings")
    print("="*60)
    
    pipeline = TTSPipeline()
    
    # List available voices
    voices = pipeline.get_available_voices()
    print(f"\n🎙️  Found {len(voices)} available voices")
    
    # Configure voice settings
    pipeline.configure_voice(rate=120, volume=0.8)
    
    text = "This speech uses custom rate and volume settings."
    pipeline.process_and_speak(text)


def run_all_examples():
    """Run all examples"""
    print("\n🚀 TTS Pipeline - Complete Examples")
    print("="*60)
    
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Numbers and Formatting", example_with_numbers),
        ("Emotion Detection", example_emotion_detection),
        ("Batch Processing", example_batch_processing),
        ("Multi-language", example_multi_language),
        ("Complex Text", example_complex_text),
        ("Custom Voice Settings", example_custom_voice_settings),
    ]
    
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. Run all examples")
    
    choice = input("\nSelect example (0-7): ").strip()
    
    if choice == '0':
        for name, func in examples:
            try:
                func()
                input("\nPress Enter to continue to next example...")
            except Exception as e:
                print(f"❌ Error in {name}: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        idx = int(choice) - 1
        name, func = examples[idx]
        try:
            func()
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    run_all_examples()
