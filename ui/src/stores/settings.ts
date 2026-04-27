import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { config } from '@/lib/config';

export type Theme = 'light' | 'dark' | 'system';
export type Locale = 'en' | 'ckb' | 'ar' | 'tr';

interface SettingsState {
  theme: Theme;
  locale: Locale;
  defaultVoiceId?: string;
  defaultFormat: 'wav' | 'mp3' | 'flac' | 'ogg';
  defaultTier: 'draft' | 'standard' | 'studio';
  defaultSpeed: number;
  defaultPitch: number;
  defaultVolume: number;
  reduceMotion: boolean;
  highContrast: boolean;
  setTheme(theme: Theme): void;
  setLocale(locale: Locale): void;
  setDefaultVoice(id?: string): void;
  setDefaultFormat(f: SettingsState['defaultFormat']): void;
  setDefaultTier(t: SettingsState['defaultTier']): void;
  setDefaults(p: Partial<Pick<SettingsState, 'defaultSpeed' | 'defaultPitch' | 'defaultVolume'>>): void;
  setReduceMotion(v: boolean): void;
  setHighContrast(v: boolean): void;
  reset(): void;
}

const defaults = {
  theme: 'system' as Theme,
  locale: config.defaultLocale,
  defaultFormat: 'wav' as const,
  defaultTier: 'standard' as const,
  defaultSpeed: 1,
  defaultPitch: 0,
  defaultVolume: 1,
  reduceMotion: false,
  highContrast: false,
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    immer((set) => ({
      ...defaults,
      setTheme: (theme) => set((s) => void (s.theme = theme)),
      setLocale: (locale) => set((s) => void (s.locale = locale)),
      setDefaultVoice: (id) => set((s) => void (s.defaultVoiceId = id)),
      setDefaultFormat: (f) => set((s) => void (s.defaultFormat = f)),
      setDefaultTier: (t) => set((s) => void (s.defaultTier = t)),
      setDefaults: (p) =>
        set((s) => {
          if (p.defaultSpeed !== undefined) s.defaultSpeed = p.defaultSpeed;
          if (p.defaultPitch !== undefined) s.defaultPitch = p.defaultPitch;
          if (p.defaultVolume !== undefined) s.defaultVolume = p.defaultVolume;
        }),
      setReduceMotion: (v) => set((s) => void (s.reduceMotion = v)),
      setHighContrast: (v) => set((s) => void (s.highContrast = v)),
      reset: () => set(() => ({ ...defaults })),
    })),
    { name: config.storage.settings },
  ),
);
