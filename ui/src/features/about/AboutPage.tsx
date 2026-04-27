import { config } from '@/lib/config';
import { Card, CardContent } from '@/components/ui/card';
import { AudioWaveform } from 'lucide-react';

export function AboutPage() {
  return (
    <div className="container mx-auto max-w-2xl space-y-6 p-6">
      <Card>
        <CardContent className="space-y-4 p-8">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-info shadow-lg">
              <AudioWaveform className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">{config.appName}</h1>
              <p className="text-sm text-muted-foreground">Version {config.version}</p>
            </div>
          </div>
          <p className="text-sm leading-relaxed text-muted-foreground">
            A modern, accessible, fully self-hosted React user interface for the
            <strong className="text-foreground"> eng-tts </strong> engine. Built with React 19,
            Vite, Tailwind CSS, Radix UI, TanStack Query, Zustand, and WaveSurfer.js.
          </p>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <Field label="Engine" value="eng-tts" />
            <Field label="Model" value="Piper ONNX" />
            <Field label="API" value={config.apiBaseUrl} />
            <Field label="PWA" value="Offline-ready" />
            <Field label="Locale" value={config.defaultLocale} />
            <Field label="Build" value={import.meta.env.MODE} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border bg-card p-3">
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="mt-1 truncate font-mono">{value}</div>
    </div>
  );
}
