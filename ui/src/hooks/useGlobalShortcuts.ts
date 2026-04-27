import { useHotkeys } from 'react-hotkeys-hook';
import { useTheme } from 'next-themes';
import { useNavigate } from 'react-router-dom';
import { useUiStore } from '@/stores/ui';
import { useSynthesize } from '@/hooks/useSynthesize';
import { config } from '@/lib/config';

export function useGlobalShortcuts() {
  const togglePalette = useUiStore((s) => s.togglePalette);
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();
  const synth = useSynthesize();

  useHotkeys(config.shortcuts.palette, (e) => { e.preventDefault(); togglePalette(); }, { enableOnFormTags: true });
  useHotkeys(config.shortcuts.synth, (e) => { e.preventDefault(); synth.mutate({}); }, { enableOnFormTags: true });
  useHotkeys(config.shortcuts.settings, (e) => { e.preventDefault(); navigate('/settings'); }, { enableOnFormTags: true });
  useHotkeys(config.shortcuts.toggleTheme, (e) => {
    e.preventDefault();
    setTheme(theme === 'dark' ? 'light' : 'dark');
  }, { enableOnFormTags: true });
}
