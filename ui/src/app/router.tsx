import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { StudioPage } from '@/features/studio/StudioPage';
import { VoicesPage } from '@/features/voices/VoicesPage';
import { CharactersPage } from '@/features/characters/CharactersPage';
import { ComparePage } from '@/features/compare/ComparePage';
import { VoiceLabPage } from '@/features/voice-lab/VoiceLabPage';
import { ProjectsPage } from '@/features/projects/ProjectsPage';
import { AnalyzerPage } from '@/features/analyzer/AnalyzerPage';
import { PipelinePage } from '@/features/pipeline/PipelinePage';
import { WorkflowPage } from '@/features/workflow/WorkflowPage';
import { HistoryPage } from '@/features/history/HistoryPage';
import { SettingsPage } from '@/features/settings/SettingsPage';
import { DocsPage } from '@/features/docs/DocsPage';
import { AboutPage } from '@/features/about/AboutPage';
import { NotFoundPage } from '@/features/common/NotFoundPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <StudioPage /> },
      { path: 'voices', element: <VoicesPage /> },
      { path: 'characters', element: <CharactersPage /> },
      { path: 'compare', element: <ComparePage /> },
      { path: 'voice-lab', element: <VoiceLabPage /> },
      { path: 'projects', element: <ProjectsPage /> },
      { path: 'analyzer', element: <AnalyzerPage /> },
      { path: 'pipeline', element: <PipelinePage /> },
      { path: 'workflow', element: <WorkflowPage /> },
      { path: 'history', element: <HistoryPage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: 'docs', element: <DocsPage /> },
      { path: 'about', element: <AboutPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
