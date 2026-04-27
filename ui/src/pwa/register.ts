import { registerSW } from 'virtual:pwa-register';
import { toast } from 'sonner';

if ('serviceWorker' in navigator) {
  const updateSW = registerSW({
    immediate: true,
    onNeedRefresh() {
      toast.info('Applying latest TTS Studio update...');
      void updateSW(true);
    },
    onOfflineReady() {
      toast.success('TTS Studio is ready for offline use.');
    },
    onRegisterError(error) {
      console.warn('[pwa] service worker registration failed', error);
    },
  });
}
