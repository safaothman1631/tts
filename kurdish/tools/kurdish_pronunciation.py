"""
Kurdish to Phonetic English Pronunciation Converter
Converts Kurdish text to phonetic English for better TTS pronunciation
"""

# Kurdish to English phonetic mapping
KURDISH_TO_PHONETIC = {
    # پیتە تاکەکان / Single letters
    'ئ': '',
    'ا': 'aa',
    'ب': 'b',
    'پ': 'p',
    'ت': 't',
    'ج': 'j',
    'چ': 'ch',
    'ح': 'h',
    'خ': 'kh',
    'د': 'd',
    'ر': 'r',
    'ڕ': 'rr',
    'ز': 'z',
    'ژ': 'zh',
    'س': 's',
    'ش': 'sh',
    'ع': 'a',
    'غ': 'gh',
    'ف': 'f',
    'ڤ': 'v',
    'ق': 'q',
    'ک': 'k',
    'گ': 'g',
    'ل': 'l',
    'ڵ': 'll',
    'م': 'm',
    'ن': 'n',
    'ه': 'h',
    'ە': 'a',
    'و': 'w',
    'ۆ': 'o',
    'وو': 'oo',
    'ی': 'ee',
    'ێ': 'ay',
    
    # کۆمەڵە پیت / Letter combinations
    'ەو': 'aw',
    'ەی': 'ay',
}

# وشە بە وشە / Word by word mapping (for better accuracy)
KURDISH_WORDS = {
    # ڕێزکردن / Greetings
    'سڵاو': 'sllaw',
    'سلاو': 'sllaw',
    'چۆنی': 'chonee',
    'چونی': 'chonee',
    'باش': 'bash',
    'بەیانی': 'bayanee',
    'ئێوارە': 'aywara',
    'شەو': 'shaw',
    'خۆش': 'khosh',
    'سوپاس': 'supas',
    'خواحافیز': 'khwa hafiz',
    
    # جێگەکان / Places
    'کوردستان': 'koordistan',
    'گوند': 'gond',
    'شار': 'shar',
    
    # خێزان / Family
    'دایک': 'dayk',
    'باوک': 'bawk',
    'کوڕ': 'korr',
    'کچ': 'kch',
    'برا': 'bra',
    'خوشک': 'khoshk',
    
    # ناوەکان / Names
    'ئارمانج': 'armanj',
    
    # سیفەتەکان / Adjectives
    'بچووک': 'bchook',
    'گەورە': 'gawra',
    'جوان': 'jwan',
    'خراپ': 'khrap',
    'تاریک': 'tareek',
    'ڕوون': 'roon',
    'ڕووناک': 'roonnak',
    
    # کردارەکان / Verbs
    'هەبوو': 'habu',
    'دەکات': 'dakat',
    'دەڵێت': 'dallayt',
    'دەترسا': 'datrsa',
    'فێربوو': 'fayrbu',
    
    # ئەوانی تر / Others
    'مەهربان': 'mahraban',
    'گەنج': 'ganj',
    'دڵ': 'dll',
    'قەوی': 'qawee',
    'ترس': 'tras',
    'شەو': 'shaw',
    'ڕۆژ': 'rozh',
    'من': 'man',
    'تۆ': 'to',
    'ئەو': 'aw',
    'ئێمە': 'ayma',
    'ئێوە': 'aywa',
    'ئەوان': 'awan',
    
    # ڕستەکانی باو / Common phrases
    'چۆنیت': 'choneet',
    'زۆر باش': 'zor bash',
    'من دڵ قەویەم': 'man dll qaweyam',
    'من ڕووناکم': 'man roonakam',
    'من تەنیا نیم': 'man tanya neem',
}


def convert_kurdish_to_phonetic(text):
    """
    Convert Kurdish text to phonetic English
    
    Args:
        text (str): Kurdish text
        
    Returns:
        str: Phonetic English text
    """
    # پێشتر وشە بە وشە / First try word by word
    result = text
    for kurdish, phonetic in KURDISH_WORDS.items():
        result = result.replace(kurdish, phonetic)
    
    # پاشان پیت بە پیت / Then letter by letter for remaining
    for kurdish, phonetic in KURDISH_TO_PHONETIC.items():
        result = result.replace(kurdish, phonetic)
    
    return result


def speak_kurdish_phonetic(text, save_file=None):
    """
    Speak Kurdish text using phonetic conversion
    
    Args:
        text (str): Kurdish text
        save_file (str): Optional file path to save audio
    """
    from gtts import gTTS
    import os
    
    # گۆڕین بۆ فۆنێتیک / Convert to phonetic
    phonetic_text = convert_kurdish_to_phonetic(text)
    
    print(f"📝 کوردی: {text}")
    print(f"🔤 فۆنێتیک: {phonetic_text}")
    
    # دروستکردنی دەنگ / Create speech
    tts = gTTS(text=phonetic_text, lang='en', slow=False)
    
    if save_file:
        tts.save(save_file)
        print(f"💾 هەڵگیرا: {save_file}")
        os.system(f'start {save_file}')
    else:
        tts.save('temp_kurdish.mp3')
        os.system('start temp_kurdish.mp3')
    
    return phonetic_text


# نموونەکان / Examples
if __name__ == "__main__":
    print("=" * 60)
    print("🎤 Kurdish Pronunciation Converter")
    print("=" * 60)
    
    # نموونە ١ / Example 1
    print("\n1️⃣ نموونەی سادە:")
    speak_kurdish_phonetic("سڵاو چۆنیت برا", "output/example1.mp3")
    
    # نموونە ٢ / Example 2
    print("\n2️⃣ نموونەی درێژتر:")
    speak_kurdish_phonetic("بەیانی باش، ڕۆژت خۆش بێت", "output/example2.mp3")
    
    # نموونە ٣ / Example 3
    print("\n3️⃣ چیرۆکی ئارمانج:")
    story = "لە گوندێکی بچووک لە کوردستان، کوڕێک هەبوو بە ناوی ئارمانج"
    speak_kurdish_phonetic(story, "output/armanj_phonetic.mp3")
    
    print("\n✅ تەواو بوو!")
