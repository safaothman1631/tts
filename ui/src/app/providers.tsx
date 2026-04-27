import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider, useTheme } from 'next-themes';
import { I18nextProvider } from 'react-i18next';
import { useEffect } from 'react';
import i18n, { isRtl } from '@/i18n';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Toaster } from '@/components/ui/toaster';
import { useSettingsStore } from '@/stores/settings';
import { config } from '@/lib/config';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, err) => {
        const status = (err as { status?: number })?.status;
        if (status === 401 || status === 403 || status === 404) return false;
        return failureCount < 2;
      },
      refetchOnWindowFocus: false,
      staleTime: 30_000,
    },
  },
});

function PreferenceSync() {
  const { setTheme } = useTheme();
  const { highContrast, locale, reduceMotion, theme } = useSettingsStore();

  useEffect(() => {
    void i18n.changeLanguage(locale);
    const dir = isRtl(locale) ? 'rtl' : 'ltr';
    document.documentElement.dir = dir;
    document.documentElement.lang = locale;
  }, [locale]);

  useEffect(() => {
    setTheme(theme);
  }, [setTheme, theme]);

  useEffect(() => {
    document.documentElement.dataset.contrast = highContrast ? 'high' : 'normal';
    document.documentElement.dataset.motion = reduceMotion ? 'reduced' : 'normal';
  }, [highContrast, reduceMotion]);

  return null;
}

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <I18nextProvider i18n={i18n}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <TooltipProvider delayDuration={150}>
            <PreferenceSync />
            {children}
            <Toaster />
            {config.enableDevtools && <ReactQueryDevtools initialIsOpen={false} buttonPosition="bottom-left" />}
          </TooltipProvider>
        </ThemeProvider>
      </I18nextProvider>
    </QueryClientProvider>
  );
}
