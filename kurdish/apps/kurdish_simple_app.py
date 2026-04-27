"""
ئەپی ساکاری دەنگی کوردی
Simple Kurdish Voice App - بە دەنگ!
"""

from gtts import gTTS
import os
import time

def speak_kurdish_text(text):
    """دەنگدانەوەی دەقی کوردی بە دەنگی عەرەبی"""
    try:
        print(f"\n🎤 دەنگدانەوە: {text}")
        tts = gTTS(text=text, lang='ar', slow=False)
        temp_file = "output/temp_kurdish.mp3"
        tts.save(temp_file)
        print(f"✅ فایل دروستکرا")
        print(f"▶️ لێدانی دەنگ...")
        os.system(f'start {temp_file}')
        time.sleep(2)  # چاوەڕێ بۆ لێدانی دەنگ
        return True
    except Exception as e:
        print(f"❌ هەڵە: {e}")
        return False

def main():
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🎤 ئەپی دەنگی کوردی - Kurdish Voice App 🎤  ".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    
    while True:
        print("\n" + "─" * 60)
        print("بژاردەکان / Options:")
        print("─" * 60)
        print("1️⃣  دەنگدانەوەی دەقێک (Speak text)")
        print("2️⃣  نموونەکان (Examples)")
        print("0️⃣  دەرچوون (Exit)")
        print("─" * 60)
        
        choice = input("\n➤ هەڵبژێرە / Choose: ").strip()
        
        if choice == "0":
            print("\n👋 خوات لەگەڵ بێت! / Goodbye!")
            break
            
        elif choice == "1":
            print("\n📝 دەقەکەت بنووسە (بە کوردی):")
            text = input("➤ ")
            if text.strip():
                speak_kurdish_text(text)
            else:
                print("❌ تکایە دەقێک بنووسە!")
                
        elif choice == "2":
            print("\n📚 نموونەکانی کوردی:")
            examples = {
                "1": "سڵاو! چۆنی؟",
                "2": "بەیانی باش! ڕۆژت خۆش بێت",
                "3": "ئێوارەتان باش",
                "4": "شەوتان خۆش",
                "5": "خواحافیز! خوات لەگەڵ بێت",
                "6": "زۆر سوپاس",
                "7": "ببورە",
                "8": "کوردستان خاکێکی جوانە"
            }
            
            print("")
            for key, text in examples.items():
                print(f"   {key}. {text}")
            print("   0. گەڕانەوە / Back")
            
            ex_choice = input("\n➤ هەڵبژێرە / Choose: ").strip()
            
            if ex_choice in examples:
                text = examples[ex_choice]
                print(f"\n🎯 {text}")
                speak_kurdish_text(text)
            elif ex_choice != "0":
                print("❌ هەڵبژاردنێکی نادروست!")
        
        else:
            print("❌ هەڵبژاردنێکی نادروست! تکایە 0، 1، یان 2 هەڵبژێرە")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 خوات لەگەڵ بێت! / Goodbye!")
    except Exception as e:
        print(f"\n❌ هەڵە: {e}")
