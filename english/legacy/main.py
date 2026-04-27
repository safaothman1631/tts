"""
Main application for Text-to-Speech with NLP Pipeline
"""

import argparse
from tts_pipeline import TTSPipeline


def main():
    parser = argparse.ArgumentParser(
        description="Text-to-Speech with NLP Processing Pipeline"
    )
    
    parser.add_argument(
        'text',
        nargs='?',
        type=str,
        help='Text to convert to speech'
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Input text file'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output filename (without extension)'
    )
    
    parser.add_argument(
        '-s', '--save',
        action='store_true',
        help='Save to file instead of playing'
    )
    
    parser.add_argument(
        '-e', '--engine',
        type=str,
        choices=['pyttsx3', 'gtts'],
        default='pyttsx3',
        help='TTS engine to use'
    )
    
    parser.add_argument(
        '--no-emotion',
        action='store_true',
        help='Disable emotion-based prosody adjustment'
    )
    
    parser.add_argument(
        '--voices',
        action='store_true',
        help='List available voices'
    )
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = TTSPipeline(engine_type=args.engine)
    
    # List voices if requested
    if args.voices:
        print("🎙️  Available Voices:")
        voices = pipeline.get_available_voices()
        for i, voice in enumerate(voices, 1):
            print(f"{i}. {voice['name']}")
            print(f"   ID: {voice['id']}")
            print(f"   Languages: {voice.get('languages', 'N/A')}")
            print()
        return
    
    # Get text from file or argument
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return
    elif args.text:
        text = args.text
    else:
        # Interactive mode
        print("🎤 Text-to-Speech with NLP Pipeline")
        print("=" * 50)
        text = input("\nEnter text to convert to speech:\n> ")
    
    if not text or not text.strip():
        print("❌ No text provided!")
        return
    
    use_emotion = not args.no_emotion
    
    # Process and speak or save
    try:
        if args.save:
            pipeline.process_and_save(
                text,
                output_filename=args.output,
                use_emotion=use_emotion
            )
        else:
            pipeline.process_and_speak(text, use_emotion=use_emotion)
    except Exception as e:
        print(f"❌ Error: {e}")


def interactive_demo():
    """Run interactive demonstration"""
    print("🎤 Text-to-Speech with NLP Pipeline - Interactive Demo")
    print("=" * 60)
    
    pipeline = TTSPipeline()
    
    # Demo texts
    demo_texts = [
        "Hello! I'm excited to demonstrate this advanced text-to-speech system with natural language processing.",
        "Dr. Smith earned $150,000 in 2023. That's a 25% increase from the previous year!",
        "I'm feeling sad today. The weather is gloomy and nothing seems to go right.",
        "Call me at 555-1234 or email john.doe@example.com for more information."
    ]
    
    print("\n📝 Demo Texts:")
    for i, text in enumerate(demo_texts, 1):
        print(f"{i}. {text}")
    
    print("\nOptions:")
    print("1-4: Process and speak demo text")
    print("5: Enter custom text")
    print("6: List available voices")
    print("0: Exit")
    
    while True:
        choice = input("\nSelect option: ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice in ['1', '2', '3', '4']:
            idx = int(choice) - 1
            text = demo_texts[idx]
            print(f"\n🎯 Processing: {text}")
            pipeline.process_and_speak(text)
        elif choice == '5':
            text = input("Enter your text: ").strip()
            if text:
                save = input("Save to file? (y/n): ").strip().lower() == 'y'
                if save:
                    filename = input("Filename (optional): ").strip() or None
                    pipeline.process_and_save(text, output_filename=filename)
                else:
                    pipeline.process_and_speak(text)
        elif choice == '6':
            voices = pipeline.get_available_voices()
            print("\n🎙️  Available Voices:")
            for i, voice in enumerate(voices, 1):
                print(f"{i}. {voice['name']}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        main()
    else:
        interactive_demo()
