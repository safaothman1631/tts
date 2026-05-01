/**
 * Centralized client-side configuration.
 * All values can be overridden via Vite env vars (VITE_*).
 */

const rawApiBaseUrl = import.meta.env.VITE_API_URL || '';
const isLocalApp = ['127.0.0.1', 'localhost'].includes(location.hostname);
const isLocalApi = /^https?:\/\/(127\.0\.0\.1|localhost):8765\/?$/.test(rawApiBaseUrl);
const apiBaseUrl = isLocalApp && isLocalApi ? '/api' : rawApiBaseUrl || '/api';

export const config = {
  appName: 'TTS Studio',
  version: '0.1.0',
  apiBaseUrl,
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
