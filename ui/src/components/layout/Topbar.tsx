import { Globe, Moon, Sun, Command, Github } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { useUiStore } from '@/stores/ui';
import { useSettingsStore } from '@/stores/settings';
import { useHealthQuery } from '@/hooks/queries';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';
import { backendStatusLabel } from '@/lib/backend-status';
import { cn } from '@/lib/utils';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';

export function Topbar() {
  const { t } = useTranslation();
  const { theme, setTheme: setThemeClass } = useTheme();
  const togglePalette = useUiStore((s) => s.togglePalette);
  const { locale, setLocale, setTheme: setStoredTheme } = useSettingsStore();
  const health = useHealthQuery();
  const online = useOnlineStatus();
  const currentTheme = theme === 'dark' ? 'dark' : 'light';
  const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b bg-background/60 px-4 backdrop-blur-xl">
      <div className="flex items-center gap-3">
        <HealthPill online={online} status={health.data?.status ?? 'down'} t={t} />
      </div>

      <div className="flex items-center gap-1">
        <Button
          variant="outline"
          size="sm"
          className="hidden h-8 gap-2 ps-2 pe-3 text-xs text-muted-foreground sm:inline-flex"
          onClick={() => togglePalette(true)}
          aria-label={t('actions.openPalette')}
        >
          <Command className="h-3.5 w-3.5" />
          <span>{t('actions.search')}</span>
          <span className="ms-2 flex items-center gap-0.5">
            <kbd className="rounded border bg-muted px-1.5 py-0.5 font-mono text-[10px]">⌘</kbd>
            <kbd className="rounded border bg-muted px-1.5 py-0.5 font-mono text-[10px]">K</kbd>
          </span>
        </Button>

        <Select value={locale} onValueChange={(v) => setLocale(v as 'en' | 'ckb' | 'ar' | 'tr')}>
          <SelectTrigger className="h-8 w-auto gap-1.5 border-0 bg-transparent px-2 text-xs">
            <Globe className="h-3.5 w-3.5" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="en">English</SelectItem>
            <SelectItem value="ckb">کوردی</SelectItem>
            <SelectItem value="ar">العربية</SelectItem>
            <SelectItem value="tr">Türkçe</SelectItem>
          </SelectContent>
        </Select>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => {
                setStoredTheme(nextTheme);
                setThemeClass(nextTheme);
              }}
              aria-label={t('actions.toggleTheme')}
            >
              {currentTheme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          </TooltipTrigger>
          <TooltipContent>{t('actions.toggleTheme')}</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button asChild variant="ghost" size="icon" className="h-8 w-8">
              <a href="https://github.com" target="_blank" rel="noreferrer" aria-label="GitHub">
                <Github className="h-4 w-4" />
              </a>
            </Button>
          </TooltipTrigger>
          <TooltipContent>GitHub</TooltipContent>
        </Tooltip>
      </div>
    </header>
  );
}

function HealthPill({ online, status, t }: { online: boolean; status: string; t: (k: string) => string }) {
  const label = backendStatusLabel(status, online);
  const color = label === 'Online' ? 'bg-success' : label === 'Degraded' ? 'bg-warning' : 'bg-destructive';
  const translated = label === 'Online'
    ? t('common.online')
    : label === 'Degraded'
      ? t('common.degraded')
      : t('common.offline');
  return (
    <div className="flex items-center gap-2 rounded-full border bg-card/60 px-3 py-1 text-xs">
      <span className={cn('h-2 w-2 animate-pulse rounded-full', color)} />
      <span className="text-muted-foreground">{translated}</span>
    </div>
  );
}
