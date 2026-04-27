import { Command } from 'cmdk';
import { useNavigate } from 'react-router-dom';
import { useTheme } from 'next-themes';
import { useTranslation } from 'react-i18next';
import {
  AudioWaveform, FolderOpen, History, Mic2, ScanText, Settings,
  Sparkles, Sun, Moon, Globe, BookOpen, Info, GitBranch, Play, Route,
} from 'lucide-react';
import { useUiStore } from '@/stores/ui';
import { useSettingsStore } from '@/stores/settings';
import { useSynthesize } from '@/hooks/useSynthesize';
import { Dialog, DialogContent } from '@/components/ui/dialog';

export function CommandPalette() {
  const { paletteOpen, togglePalette } = useUiStore();
  const navigate = useNavigate();
  const { theme, setTheme } = useTheme();
  const { setLocale } = useSettingsStore();
  const synth = useSynthesize();
  const { t } = useTranslation();

  const go = (path: string) => {
    togglePalette(false);
    navigate(path);
  };

  return (
    <Dialog open={paletteOpen} onOpenChange={(o) => togglePalette(o)}>
      <DialogContent className="max-w-2xl overflow-hidden p-0">
        <Command className="[&_[cmdk-input]]:px-4 [&_[cmdk-input]]:py-3 [&_[cmdk-input]]:text-sm">
          <Command.Input
            placeholder={`${t('actions.search')}...`}
            className="w-full border-b bg-transparent outline-none placeholder:text-muted-foreground"
          />
          <Command.List className="max-h-[400px] overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
              No results.
            </Command.Empty>

            <Command.Group heading="Navigation" className="text-xs text-muted-foreground [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5">
              <Item icon={Sparkles} label={t('nav.studio')} onSelect={() => go('/')} shortcut="G S" />
              <Item icon={AudioWaveform} label={t('nav.voices')} onSelect={() => go('/voices')} shortcut="G V" />
              <Item icon={Mic2} label={t('nav.voiceLab')} onSelect={() => go('/voice-lab')} />
              <Item icon={FolderOpen} label={t('nav.projects')} onSelect={() => go('/projects')} />
              <Item icon={ScanText} label={t('nav.analyzer')} onSelect={() => go('/analyzer')} />
              <Item icon={GitBranch} label={t('nav.pipeline')} onSelect={() => go('/pipeline')} />
              <Item icon={Route} label={t('nav.workflow')} onSelect={() => go('/workflow')} />
              <Item icon={History} label={t('nav.history')} onSelect={() => go('/history')} />
              <Item icon={Settings} label={t('nav.settings')} onSelect={() => go('/settings')} shortcut="⌘ ," />
              <Item icon={BookOpen} label={t('nav.docs')} onSelect={() => go('/docs')} />
              <Item icon={Info} label={t('nav.about')} onSelect={() => go('/about')} />
            </Command.Group>

            <Command.Group heading="Actions" className="text-xs text-muted-foreground [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5">
              <Item
                icon={Play}
                label={t('actions.synthesize')}
                onSelect={() => { togglePalette(false); synth.mutate({}); }}
                shortcut="⌘ ⏎"
              />
              <Item
                icon={theme === 'dark' ? Sun : Moon}
                label={t('actions.toggleTheme')}
                onSelect={() => { setTheme(theme === 'dark' ? 'light' : 'dark'); togglePalette(false); }}
              />
              <Item
                icon={Globe}
                label="English"
                onSelect={() => { setLocale('en'); togglePalette(false); }}
              />
              <Item
                icon={Globe}
                label="کوردی (Kurdish)"
                onSelect={() => { setLocale('ckb'); togglePalette(false); }}
              />
            </Command.Group>
          </Command.List>
        </Command>
      </DialogContent>
    </Dialog>
  );
}

function Item({
  icon: Icon, label, onSelect, shortcut,
}: { icon: React.ComponentType<{ className?: string }>; label: string; onSelect: () => void; shortcut?: string }) {
  return (
    <Command.Item
      onSelect={onSelect}
      className="flex cursor-pointer items-center gap-3 rounded-md px-2 py-2 text-sm aria-selected:bg-accent aria-selected:text-accent-foreground"
    >
      <Icon className="h-4 w-4 text-muted-foreground" />
      <span className="flex-1">{label}</span>
      {shortcut && (
        <span className="text-[11px] text-muted-foreground">{shortcut}</span>
      )}
    </Command.Item>
  );
}
