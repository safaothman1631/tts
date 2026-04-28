/**
 * Centralized client-side configuration.
 * All values can be overridden via Vite env vars (VITE_*).
 */

export const config = {
  appName: 'TTS Studio',
  version: '0.1.0',
  apiBaseUrl: import.meta.env.VITE_API_URL || '/api',
  wsBaseUrl: import.meta.env.VITE_WS_URL || `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`,
  defaultLocale: (import.meta.env.VITE_DEFAULT_LOCALE as 'en' | 'ckb' | 'ar' | 'tr') || 'en',
  enableDevtools: import.meta.env.DEV,
  storage: {
    settings: 'tts-studio:settings',
    history: 'tts-studio:history',
    apiToken: 'tts-studio:token',
    locale: 'tts-studio:locale',
    theme: 'tts-studio:theme',
  },
  audio: {
    defaultFormat: 'wav' as const,
    sampleRate: 22050,
    maxHistorySize: 200,
  },
  shortcuts: {
    palette: 'mod+k',
    play: 'space',
    synth: 'mod+enter',
    save: 'mod+s',
    newDoc: 'mod+n',
    settings: 'mod+,',
    toggleTheme: 'mod+shift+l',
  },
} as const;

export type AppConfig = typeof config;
