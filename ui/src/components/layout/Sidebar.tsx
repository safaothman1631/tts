import { NavLink } from 'react-router-dom';
import {
  AudioWaveform,
  Mic2,
  FolderOpen,
  Settings,
  History,
  Sparkles,
  GitBranch,
  Route,
  BookOpen,
  Info,
  ScanText,
  Globe2,
  PanelLeftClose,
  PanelLeftOpen,
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useUiStore } from '@/stores/ui';
import { cn } from '@/lib/utils';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { Button } from '@/components/ui/button';

interface NavItem {
  to: string;
  label: 'studio' | 'voices' | 'characters' | 'voiceLab' | 'projects' | 'analyzer' | 'pipeline' | 'workflow' | 'history' | 'settings' | 'docs' | 'about';
  icon: React.ComponentType<{ className?: string }>;
}

const items: NavItem[] = [
  { to: '/', label: 'studio', icon: Sparkles },
  { to: '/voices', label: 'voices', icon: AudioWaveform },
  { to: '/characters', label: 'characters', icon: Globe2 },
  { to: '/voice-lab', label: 'voiceLab', icon: Mic2 },
  { to: '/projects', label: 'projects', icon: FolderOpen },
  { to: '/analyzer', label: 'analyzer', icon: ScanText },
  { to: '/pipeline', label: 'pipeline', icon: GitBranch },
  { to: '/workflow', label: 'workflow', icon: Route },
  { to: '/history', label: 'history', icon: History },
  { to: '/settings', label: 'settings', icon: Settings },
  { to: '/docs', label: 'docs', icon: BookOpen },
  { to: '/about', label: 'about', icon: Info },
];

export function Sidebar() {
  const { t } = useTranslation();
  const { sidebarOpen, toggleSidebar } = useUiStore();

  return (
    <aside
      className={cn(
        'fixed inset-y-0 start-0 z-30 flex flex-col border-e bg-card/40 backdrop-blur-xl transition-[width] duration-200',
        sidebarOpen ? 'w-64' : 'w-16',
      )}
    >
      <div className="flex h-14 items-center justify-between border-b px-3">
        {sidebarOpen ? (
          <div className="flex items-center gap-2">
            <Logo />
            <div>
              <div className="text-sm font-bold leading-none">TTS Studio</div>
              <div className="text-[10px] text-muted-foreground">v0.1.0</div>
            </div>
          </div>
        ) : (
          <div className="mx-auto"><Logo /></div>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={() => toggleSidebar()}
          aria-label="Toggle sidebar"
        >
          {sidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeftOpen className="h-4 w-4" />}
        </Button>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-2">
        {items.map((item) => {
          const link = (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                cn(
                  'group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
                )
              }
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {sidebarOpen && <span>{t(`nav.${item.label}`)}</span>}
            </NavLink>
          );
          return sidebarOpen ? (
            link
          ) : (
            <Tooltip key={item.to}>
              <TooltipTrigger asChild>{link}</TooltipTrigger>
              <TooltipContent side="right">{t(`nav.${item.label}`)}</TooltipContent>
            </Tooltip>
          );
        })}
      </nav>

      {sidebarOpen && (
        <div className="border-t p-3 text-[11px] text-muted-foreground">
          <div className="flex items-center gap-1">
            <kbd className="rounded border bg-muted px-1.5 py-0.5 font-mono text-[10px]">Ctrl</kbd>
            <kbd className="rounded border bg-muted px-1.5 py-0.5 font-mono text-[10px]">K</kbd>
            <span className="ms-1">{t('actions.openPalette')}</span>
          </div>
        </div>
      )}
    </aside>
  );
}

function Logo() {
  return (
    <div className="flex h-8 w-8 items-center justify-center rounded-md bg-gradient-to-br from-primary to-info shadow-md">
      <AudioWaveform className="h-4 w-4 text-white" />
    </div>
  );
}
