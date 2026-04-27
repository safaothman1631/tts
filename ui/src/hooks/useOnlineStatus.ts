import { useEffect, useState } from 'react';

function readOnlineStatus(): boolean {
  if (typeof navigator === 'undefined') return true;
  return navigator.onLine;
}

export function useOnlineStatus(): boolean {
  const [online, setOnline] = useState(readOnlineStatus);

  useEffect(() => {
    const sync = () => setOnline(readOnlineStatus());
    window.addEventListener('online', sync);
    window.addEventListener('offline', sync);
    sync();
    return () => {
      window.removeEventListener('online', sync);
      window.removeEventListener('offline', sync);
    };
  }, []);

  return online;
}
