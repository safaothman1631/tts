/**
 * Curated sample texts for quick-fill across the UI (Studio, Analyzer,
 * Compare, VoiceLab, Voices). Five categories that exercise different
 * NLP/TTS code paths so users can audition voices and pipelines fast.
 */

export type SampleTextCategory =
  | 'greeting'
  | 'story'
  | 'technical'
  | 'numbers'
  | 'dialogue';

export interface SampleText {
  id: string;
  category: SampleTextCategory;
  label: string;
  text: string;
  language?: string;
}

export const SAMPLE_TEXTS: SampleText[] = [
  {
    id: 'greeting',
    category: 'greeting',
    label: 'Greeting',
    language: 'en',
    text: "Hello! Welcome to TTS Studio. I'm so glad you're here — let's see how natural this voice can sound.",
  },
  {
    id: 'story',
    category: 'story',
    label: 'Story',
    language: 'en',
    text:
      'Once upon a time, in a small village by the sea, there lived a curious little fox who dreamed of sailing beyond the horizon. ' +
      'Every morning she would climb the tallest hill and watch the fishing boats vanish into the silver mist.',
  },
  {
    id: 'technical',
    category: 'technical',
    label: 'Technical',
    language: 'en',
    text:
      'Researchers at MIT announced a transformer-based acoustic model that achieves 4.2 mean opinion score on the LJSpeech benchmark, ' +
      'while running inference at 0.18 real-time factor on a single NVIDIA RTX 4090 GPU.',
  },
  {
    id: 'numbers',
    category: 'numbers',
    label: 'Numbers & dates',
    language: 'en',
    text:
      'Your appointment is confirmed for Tuesday, March 12th, 2026 at 9:45 a.m. ' +
      'Total amount: $1,249.99, including 7.5% tax. Reference number: TX-00471-B.',
  },
  {
    id: 'dialogue',
    category: 'dialogue',
    label: 'Dialogue',
    language: 'en',
    text:
      '"Are you sure about this?" she asked, raising an eyebrow. ' +
      '"Absolutely," he replied with a confident grin. "I\'ve been waiting my whole life for a moment exactly like this one."',
  },
];

export function getSampleById(id: string): SampleText | undefined {
  return SAMPLE_TEXTS.find((s) => s.id === id);
}
