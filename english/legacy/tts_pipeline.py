"""
Complete TTS Pipeline integrating NLP processing and speech synthesis
"""

import json
from pathlib import Path
from datetime import datetime
from nlp_processor import NLPProcessor
from tts_engine import TTSEngine
from config import SAVE_PROCESSED_TEXT, OUTPUT_DIR


class TTSPipeline:
    """
    Complete Text-to-Speech pipeline with NLP preprocessing
    """
    
    def __init__(self, engine_type="pyttsx3"):
        self.nlp_processor = NLPProcessor()
        self.tts_engine = TTSEngine(engine_type=engine_type)
        self.output_dir = Path(OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
    
    def process_and_speak(self, text, use_emotion=True):
        """
        Process text with NLP and convert to speech
        """
        print("🔄 Processing text with NLP...")
        
        # NLP Processing
        processed_text, metadata = self.nlp_processor.process_text(text)
        
        # Display metadata
        self._display_metadata(metadata)
        
        # Determine emotion for prosody adjustment
        emotion = "neutral"
        if use_emotion and metadata['sentiment']:
            emotion = metadata['sentiment']['emotion']
        
        print(f"\n🎤 Speaking with emotion: {emotion}")
        print(f"   Language: {metadata['language']}")
        
        # Convert to speech with language support
        self.tts_engine.speak(processed_text, emotion=emotion, language=metadata['language'])
        
        return processed_text, metadata
    
    def process_and_save(self, text, output_filename=None, use_emotion=True):
        """
        Process text with NLP and save to audio file
        """
        print("🔄 Processing text with NLP...")
        
        # NLP Processing
        processed_text, metadata = self.nlp_processor.process_text(text)
        
        # Display metadata
        self._display_metadata(metadata)
        
        # Generate filename if not provided
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"speech_{timestamp}"
        
        # Determine emotion for prosody adjustment
        emotion = "neutral"
        if use_emotion and metadata['sentiment']:
            emotion = metadata['sentiment']['emotion']
        
        print(f"\n💾 Saving audio with emotion: {emotion}")
        print(f"   Language: {metadata['language']}")
        
        # Save to audio file with language support
        audio_path = self.tts_engine.save_to_file(
            processed_text, 
            output_filename, 
            emotion=emotion,
            language=metadata['language']
        )
        
        print(f"✅ Audio saved to: {audio_path}")
        
        # Save processed text and metadata if enabled
        if SAVE_PROCESSED_TEXT:
            self._save_metadata(output_filename, processed_text, metadata)
        
        return audio_path, processed_text, metadata
    
    def batch_process(self, texts, output_prefix="batch"):
        """
        Process multiple texts in batch
        """
        results = []
        
        for i, text in enumerate(texts, 1):
            print(f"\n📝 Processing text {i}/{len(texts)}...")
            filename = f"{output_prefix}_{i}"
            
            try:
                audio_path, processed_text, metadata = self.process_and_save(
                    text, 
                    output_filename=filename
                )
                results.append({
                    "index": i,
                    "success": True,
                    "audio_path": str(audio_path),
                    "metadata": metadata
                })
            except Exception as e:
                print(f"❌ Error processing text {i}: {e}")
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def _display_metadata(self, metadata):
        """Display processing metadata"""
        print(f"\n📊 Text Analysis:")
        print(f"   Language: {metadata['language']}")
        print(f"   Sentences: {metadata['sentence_count']}")
        print(f"   Original length: {metadata['original_length']} chars")
        print(f"   Processed length: {metadata['processed_length']} chars")
        
        if metadata['sentiment']:
            sentiment = metadata['sentiment']
            print(f"\n😊 Sentiment Analysis:")
            print(f"   Emotion: {sentiment['emotion']}")
            print(f"   Polarity: {sentiment['polarity']:.2f} (-1 to 1)")
            print(f"   Subjectivity: {sentiment['subjectivity']:.2f} (0 to 1)")
        
        if metadata['entities']:
            print(f"\n🏷️  Named Entities:")
            for entity in metadata['entities'][:5]:  # Show first 5
                print(f"   - {entity['text']} ({entity['type']})")
            if len(metadata['entities']) > 5:
                print(f"   ... and {len(metadata['entities']) - 5} more")
    
    def _save_metadata(self, filename, processed_text, metadata):
        """Save processed text and metadata to JSON file"""
        metadata_path = self.output_dir / f"{filename}_metadata.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "processed_text": processed_text,
            "metadata": metadata
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Metadata saved to: {metadata_path}")
    
    def get_available_voices(self):
        """Get list of available voices"""
        return self.tts_engine.get_available_voices()
    
    def configure_voice(self, voice_id=None, rate=None, volume=None):
        """Configure voice properties"""
        if voice_id:
            self.tts_engine.set_voice(voice_id)
        if rate:
            self.tts_engine.set_rate(rate)
        if volume:
            self.tts_engine.set_volume(volume)
