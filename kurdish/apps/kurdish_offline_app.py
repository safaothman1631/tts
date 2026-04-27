"""
ئەپی دەنگی کوردی - ئۆفلاین بە pyttsx3
Kurdish Voice App - Offline with pyttsx3
"""

import pyttsx3
import time

class KurdishVoiceOffline:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.setup_voice()
    
    def setup_voice(self):
        """ڕێکخستنی دەنگ"""
        # ڕێکخستنی خێرایی و قەبارە
        self.engine.setProperty('rate', 150)  # خێرایی
        self.engine.setProperty('volume', 0.9)  # قەبارە
        
        # هەوڵدان بۆ دۆزینەوەی دەنگێکی گونجاو
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
    
    def speak(self, text):
        """دەنگدانەوەی دەق"""
        try:
            print(f"🎤 دەنگدانەوە: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"❌ هەڵە: {e}")
            return False
    
    def save(self, text, filename):
        """پاشەکەوتکردنی دەنگ"""
        try:
            filepath = f"output/{filename}.wav"
            self.engine.save_to_file(text, filepath)
            self.engine.runAndWait()
            print(f"✅ پاشەکەوت کرا: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ هەڵە: {e}")
            return None

def main():
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║  🎤 ئەپی دەنگی کوردی - ئۆفلاین 🎤  ".center(70) + "║")
    print("║  Kurdish Voice App - Offline Mode  ".center(70) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    
    print("\n⚠️  تێبینی / Note:")
    print("    ئەم بەرنامەیە دەنگی ئینگلیزی بەکاردەهێنێت")
    print("    لەوانەیە کوردی بە باشی نەخوێنێتەوە")
    print("    This uses English TTS engine")
    print("    May not pronounce Kurdish well\n")
    
    voice = KurdishVoiceOffline()
    
    while True:
        print("\n" + "─" * 60)
        print("بژاردەکان / Options:")
        print("─" * 60)
        print("1️⃣  دەنگدانەوەی دەق (Speak text)")
        print("2️⃣  نموونەکان (Examples)")
        print("3️⃣  پاشەکەوتکردن (Save to file)")
        print("0️⃣  دەرچوون (Exit)")
        print("─" * 60)
        
        choice = input("\n➤ هەڵبژێرە / Choose: ").strip()
        
        if choice == "0":
            print("\n👋 خوات لەگەڵ بێت! / Goodbye!")
            break
            
        elif choice == "1":
            print("\n📝 دەقەکەت بنووسە:")
            text = input("➤ ")
            if text.strip():
                voice.speak(text)
            else:
                print("❌ تکایە دەقێک بنووسە!")
                
        elif choice == "2":
            print("\n📚 نموونەکانی کوردی:")
            examples = {
                "1": "sallaw chonee",  # سڵاو چۆنی
                "2": "bayanee bash",   # بەیانی باش
                "3": "shawtan khosh",  # شەوتان خۆش
                "4": "khwa hafiz",     # خواحافیز
                "5": "zor supas",      # زۆر سوپاس
            }
            
            print("\n   (بە نووسینی لاتینی / Latin script):")
            for key, text in examples.items():
                print(f"   {key}. {text}")
            print("   0. گەڕانەوە / Back")
            
            ex_choice = input("\n➤ هەڵبژێرە / Choose: ").strip()
            
            if ex_choice in examples:
                text = examples[ex_choice]
                voice.speak(text)
            elif ex_choice != "0":
                print("❌ هەڵبژاردنێکی نادروست!")
        
        elif choice == "3":
            print("\n📝 دەقەکەت بنووسە:")
            text = input("➤ ")
            if text.strip():
                print("📁 ناوی فایل:")
                filename = input("➤ ") or "kurdish_voice"
                voice.save(text, filename)
            else:
                print("❌ تکایە دەقێک بنووسە!")
        
        else:
            print("❌ هەڵبژاردنێکی نادروست!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 خوات لەگەڵ بێت! / Goodbye!")
    except Exception as e:
        print(f"\n❌ هەڵە: {e}")
