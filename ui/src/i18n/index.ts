import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import ar from './ar/common.json';
import en from './en/common.json';
import ckb from './ckb/common.json';
import tr from './tr/common.json';

void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      ar: { common: ar },
      en: { common: en },
      ckb: { common: ckb },
      tr: { common: tr },
    },
    fallbackLng: 'en',
    defaultNS: 'common',
    interpolation: { escapeValue: false },
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'tts-studio:locale',
      caches: ['localStorage'],
    },
  });

export const RTL_LOCALES = new Set(['ckb', 'ar', 'fa', 'he']);
export function isRtl(lng: string): boolean {
  return RTL_LOCALES.has(lng.toLowerCase().split('-')[0] ?? '');
}

export default i18n;
