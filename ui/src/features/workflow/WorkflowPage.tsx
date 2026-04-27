import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, FileText, Layers3, Sparkles, Workflow, Wrench } from 'lucide-react';

const phases = [
  {
    id: '01',
    title: 'Input & Validation',
    icon: FileText,
    points: [
      'Text/SSML is validated and normalized in the API layer.',
      'Tier/voice settings are mapped to backend-safe values.',
      'Bad requests are rejected early with clear errors.',
    ],
  },
  {
    id: '02',
    title: 'NLP Pipeline',
    icon: Layers3,
    points: [
      'Tokenizer + sentence segmentation + linguistic analysis.',
      'G2P and prosody scoring for natural output rhythm.',
      'Sentiment and frame building for acoustic inference.',
    ],
  },
  {
    id: '03',
    title: 'Acoustic Synthesis',
    icon: Sparkles,
    points: [
      'Qwen3, Piper, and fallback backends are selected by policy.',
      'Generated waveform is normalized/resampled for playback.',
      'Voice cloning path applies only when reference audio exists.',
    ],
  },
  {
    id: '04',
    title: 'Delivery & UX',
    icon: Workflow,
    points: [
      'Audio blob is stored in state and rendered in player only.',
      'No auto-download is triggered by synthesis completion.',
      'Download starts only when user clicks the dedicated button.',
    ],
  },
];

const checks = [
  'Backend health endpoint responds OK',
  'Voice catalog is loaded (online/offline-first)',
  'Synthesis response returns valid audio headers',
  'Audio player stays paused until user presses Play',
  'Download button exports file only on click',
  'Typecheck/build/e2e pass before release',
];

export function WorkflowPage() {
  return (
    <div className="container mx-auto max-w-6xl space-y-6 p-6">
      <header className="rounded-2xl border bg-gradient-to-r from-primary/10 via-cyan-400/10 to-emerald-400/10 p-6">
        <div className="mb-2 flex items-center gap-2">
          <Badge variant="secondary">Presentation Ready</Badge>
          <Badge variant="outline">Operational Workflow</Badge>
        </div>
        <h1 className="text-3xl font-bold tracking-tight">Production Workflow</h1>
        <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
          End-to-end map of how this TTS platform processes text into downloadable audio with safe UX rules,
          backend fallback logic, and release quality gates.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-2">
        {phases.map((phase) => (
          <Card key={phase.id} className="border-border/70">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-base">
                <phase.icon className="h-4 w-4 text-primary" />
                <span className="font-mono text-xs text-muted-foreground">{phase.id}</span>
                {phase.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              {phase.points.map((point) => (
                <div key={point} className="flex gap-2">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                  <span>{point}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Wrench className="h-4 w-4 text-primary" />
            Release Checklist
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-2 sm:grid-cols-2">
          {checks.map((item) => (
            <div key={item} className="flex items-center gap-2 rounded-md border bg-muted/20 px-3 py-2 text-sm">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              <span>{item}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
