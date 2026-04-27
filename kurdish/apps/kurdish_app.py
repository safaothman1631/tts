"""
ئەپی سادەی کوردی بۆ TTS
Simple Kurdish TTS App
"""

from tts_pipeline import TTSPipeline

def main():
    print("=" * 60)
    print("🎤 سیستەمی گۆڕینی نووسین بۆ دەنگ بە کوردی")
    print("🎤 Kurdish Text-to-Speech System")
    print("=" * 60)
    
    # دروستکردنی pipeline
    pipeline = TTSPipeline(engine_type="gtts")
    
    while True:
        print("\n\nبژاردەکان / Options:")
        print("1️⃣  قسەکردنی دەقێک (Speak text)")
        print("2️⃣  پاشەکەوتکردن لە فایل (Save to file)")
        print("3️⃣  نموونەکان (Examples)")
        print("0️⃣  دەرچوون (Exit)")
        
        choice = input("\nهەڵبژاردنێک بکە / Choose: ").strip()
        
        if choice == "0":
            print("\n👋 خوات لەگەڵ بێت! / Goodbye!")
            break
            
        elif choice == "1":
            print("\n📝 دەقەکەت بنووسە / Enter your text:")
            text = input("➤ ")
            if text.strip():
                print("\n🔄 پرۆسێسکردن...")
                pipeline.process_and_speak(text)
            else:
                print("❌ تکایە دەقێک بنووسە!")
                
        elif choice == "2":
            print("\n📝 دەقەکەت بنووسە / Enter your text:")
            text = input("➤ ")
            if text.strip():
                print("📁 ناوی فایل (بەتاڵی بهێڵە بۆ ناوی خۆکار):")
                filename = input("➤ ").strip()
                if not filename:
                    from datetime import datetime
                    filename = f"kurdish_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                print("\n🔄 پرۆسێسکردن و پاشەکەوتکردن...")
                pipeline.process_and_save(text, output_filename=filename)
            else:
                print("❌ تکایە دەقێک بنووسە!")
                
        elif choice == "3":
            print("\n📚 نموونەکان:")
            examples = [
                "سڵاو! چۆنی؟ خۆشحاڵم بە بینینت",
                "کوردستان خاکێکی جوانە",
                "بەیانی باش! ڕۆژت خۆش بێت",
                "زمانی کوردی زمانێکی دەوڵەمەندە",
            ]
            
            for i, ex in enumerate(examples, 1):
                print(f"   {i}. {ex}")
            
            print("\n   0. گەڕانەوە / Back")
            ex_choice = input("\nهەڵبژێرە / Choose: ").strip()
            
            if ex_choice in ["1", "2", "3", "4"]:
                idx = int(ex_choice) - 1
                text = examples[idx]
                print(f"\n🎯 {text}")
                print("🔄 پرۆسێسکردن...")
                pipeline.process_and_speak(text)
        
        else:
            print("❌ هەڵبژاردنێکی نادروست!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 خوات لەگەڵ بێت! / Goodbye!")
    except Exception as e:
        print(f"\n❌ هەڵە: {e}")
