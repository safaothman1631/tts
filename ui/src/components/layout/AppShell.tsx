import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { CommandPalette } from './CommandPalette';
import { PageTransition } from './PageTransition';
import { useUiStore } from '@/stores/ui';
import { cn } from '@/lib/utils';
import { useGlobalShortcuts } from '@/hooks/useGlobalShortcuts';

export function AppShell() {
  const sidebarOpen = useUiStore((s) => s.sidebarOpen);
  useGlobalShortcuts();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground">
      <Sidebar />
      <div
        className={cn(
          'flex flex-1 flex-col overflow-hidden transition-[margin] duration-200',
          sidebarOpen ? 'ms-64' : 'ms-16',
        )}
      >
        <Topbar />
        <main className="flex-1 overflow-y-auto">
          <PageTransition />
        </main>
      </div>
      <CommandPalette />
    </div>
  );
}
