import { useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BookOpen, Copy, Cpu, Network, ShieldCheck, HelpCircle, Sparkles, Mic, ScanText, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

import gettingStartedMd from '../../../docs/getting-started.md?raw';
import architectureMd from '../../../docs/architecture.md?raw';
import deploymentMd from '../../../docs/deployment.md?raw';

const manuals = [
  { id: 'getting-started', title: 'Getting Started', kind: 'Guide', content: gettingStartedMd },
  { id: 'architecture', title: 'Architecture', kind: 'Technical', content: architectureMd },
  { id: 'deployment', title: 'Deployment', kind: 'Ops', content: deploymentMd },
];
const fallbackManual = { id: 'fallback', title: 'Manual', kind: 'Guide', content: '' };

const systemMap = [
  { title: 'Frontend Studio', detail: 'React + Zustand + Query + WaveSurfer UX layer for synthesis and playback.' },
  { title: 'HTTP API', detail: 'FastAPI endpoints for health, voices, analysis, and WAV synthesis.' },
  { title: 'Pipeline Core', detail: 'Normalization, NLP, prosody, frame building, and backend routing.' },
  { title: 'Acoustic Engines', detail: 'Qwen3/Piper/legacy backends with safe fallback strategy.' },
];

const behaviorRules = [
  'Synthesis completion only updates the output player state.',
  'No automatic file download is triggered after synth.',
  'Download starts only when the dedicated Download button is clicked.',
  'Playback starts only when Play is clicked by user interaction.',
];

const apiFlow = [
  'POST /v1/synthesize.wav -> returns WAV bytes + sample/duration headers.',
  'GET  /v1/voices         -> returns available engines and voice models.',
  'POST /v1/analyze        -> returns token/prosody analysis for editor insight.',
  'GET  /v1/health         -> service readiness for dashboard status and checks.',
  'GET  /v1/capabilities   -> exposes Qwen3 speakers, emotions and style presets.',
  'POST /v1/voices/clone   -> creates a custom voice from a reference recording.',
  'POST /v1/warmup         -> pre-loads the default acoustic backend.',
];

const studioControls = [
  { name: 'Voice', detail: 'Pick a built-in or custom voice. Leave on Default to use the backend default.' },
  { name: 'Quality (Tier)', detail: 'Draft = fastest Piper. Standard = balanced Piper. Studio = highest-quality Qwen3 with style/emotion controls.' },
  { name: 'Format', detail: 'Output container. WAV is uncompressed and lossless and is what Studio always returns.' },
  { name: 'Language', detail: 'Hint for the acoustic backend. Especially useful with Qwen3 (Studio tier) which supports many languages.' },
  { name: 'Speed', detail: 'Playback rate (0.5×–2×). Affects the duration estimate shown next to the synthesize button.' },
  { name: 'Pitch', detail: 'Pitch shift in semitones (±12). Use sparingly to keep voices natural.' },
  { name: 'Volume', detail: 'Output gain. Values above 100% can clip; the backend applies loudness normalization unless disabled.' },
  { name: 'Style preset', detail: 'Predefined Qwen3 narration styles (Audiobook, Newscaster…). Selecting one fills the Style prompt below.' },
  { name: 'Style prompt', detail: 'Free-form description of how the voice should sound. Sent verbatim to Qwen3 as an instruction.' },
  { name: 'Speaker preset', detail: 'Named Qwen3 speaker (Ryan, Aiden, Lily…). Overrides the default speaker for the chosen voice.' },
  { name: 'Emotion', detail: 'Emotional tone hint (happy, sad, calm…) blended into the Qwen3 instruction prompt.' },
  { name: 'Segments', detail: 'Split text into multiple paragraphs, each with its own voice/tier/speed and pause.' },
  { name: 'Stream', detail: 'Receive audio chunks as soon as they are produced. Lower first-byte latency, same final size.' },
  { name: 'SSML', detail: 'Treat the input as Speech Synthesis Markup Language. Use <break>, <emphasis>, <prosody> for fine control.' },
];

const voiceLabSteps = [
  { name: 'Consent & ethics', detail: 'You must confirm you have permission to clone the voice. Misuse for impersonation is forbidden.' },
  { name: 'Record', detail: 'Capture at least 30 seconds of clean speech with one speaker. Avoid music or background noise.' },
  { name: 'Review', detail: 'Listen back. If the recording clipped or is muffled, re-record before continuing.' },
  { name: 'Name & metadata', detail: 'Name, optional description, primary language, and an optional reference transcript that improves Qwen3 clone quality.' },
  { name: 'Test & manage', detail: 'After creation, type a phrase and press Test voice. Use the new voice in Studio, start over, or delete it.' },
];

const troubleshooting = [
  { title: 'Backend offline notice in Studio', detail: 'The UI could not reach the API. Run start.bat or start-api.bat; the API listens on http://127.0.0.1:8765.' },
  { title: 'First synthesis is slow', detail: 'Models are loaded on first use. The startup warmup pre-loads the default tier; switching tier triggers a one-time load for the new backend.' },
  { title: 'Voice preview button is greyed out', detail: 'Preview requires an Online backend. Wait until the status pill switches from Offline/Degraded to Online.' },
  { title: 'Studio tier features missing', detail: 'Style/Speaker/Emotion only appear when the tier is Studio. Capabilities also need /v1/capabilities to expose presets.' },
  { title: 'Audio shows download menu', detail: 'All players use controlsList="nodownload". Use the dedicated Download button if you actually want the file.' },
  { title: 'Cloned voice sounds wrong', detail: 'Provide a clean 30–60 second sample, set the correct primary language, and add a reference transcript for best Qwen3 results.' },
];

export function DocsPage() {
  const [manualId, setManualId] = useState((manuals[0] ?? fallbackManual).id);
  const manual = useMemo(() => manuals.find((m) => m.id === manualId) ?? manuals[0] ?? fallbackManual, [manualId]);

  const copyCurrent = async () => {
    await navigator.clipboard.writeText(manual.content);
    toast.success('Documentation copied to clipboard');
  };

  return (
    <div className="container mx-auto max-w-7xl space-y-6 p-6">
      <header>
        <h1 className="text-3xl font-bold tracking-tight">Documentation Center</h1>
        <p className="text-sm text-muted-foreground">Complete technical reference for architecture, workflow, API behavior, controls, and production operations.</p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <BookOpen className="h-4 w-4 text-primary" />
              Manuals
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {manuals.map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => setManualId(m.id)}
                className={`w-full rounded-md border px-3 py-2 text-left text-sm transition-colors ${
                  manualId === m.id ? 'border-primary bg-primary/5' : 'hover:bg-accent/40'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">{m.title}</span>
                  <Badge variant="outline" className="text-[10px]">{m.kind}</Badge>
                </div>
              </button>
            ))}
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between gap-2">
                <CardTitle className="text-base">{manual.title}</CardTitle>
                <Button size="sm" variant="outline" onClick={() => void copyCurrent()}>
                  <Copy className="h-4 w-4" /> Copy
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <pre className="max-h-[420px] overflow-auto rounded-md border bg-muted/20 p-4 text-xs leading-6 text-foreground whitespace-pre-wrap">
                {manual.content}
              </pre>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-base">
                <Sparkles className="h-4 w-4 text-primary" /> Studio controls
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-2 sm:grid-cols-2">
              {studioControls.map((item) => (
                <div key={item.name} className="rounded-md border bg-muted/20 p-3 text-sm">
                  <div className="font-medium text-foreground">{item.name}</div>
                  <div className="text-muted-foreground">{item.detail}</div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-base">
                <Mic className="h-4 w-4 text-primary" /> Voice Lab steps
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-2 md:grid-cols-2">
              {voiceLabSteps.map((step, idx) => (
                <div key={step.name} className="rounded-md border bg-muted/20 p-3 text-sm">
                  <div className="flex items-center gap-2 font-medium text-foreground">
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary/15 text-[10px] text-primary">{idx + 1}</span>
                    {step.name}
                  </div>
                  <div className="mt-1 text-muted-foreground">{step.detail}</div>
                </div>
              ))}
            </CardContent>
          </Card>

          <div className="grid gap-4 xl:grid-cols-2">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base"><Cpu className="h-4 w-4 text-primary" /> System Logic</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-muted-foreground">
                {systemMap.map((item) => (
                  <div key={item.title} className="rounded-md border bg-muted/20 p-3">
                    <div className="font-medium text-foreground">{item.title}</div>
                    <div>{item.detail}</div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base"><Network className="h-4 w-4 text-primary" /> API Workflow</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-muted-foreground">
                {apiFlow.map((item) => (
                  <div key={item} className="flex gap-2 rounded-md border bg-muted/20 p-3 font-mono text-xs">
                    <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                    <span>{item}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <ScanText className="h-4 w-4 text-primary" /> Analyzer guide
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-muted-foreground">
                <p>The Analyzer runs the full NLP pipeline on your text and returns four views:</p>
                <ul className="list-disc space-y-1 pl-5">
                  <li><strong>Tokens</strong> — spaCy tokens with POS type and per-syllable stress.</li>
                  <li><strong>Phonemes</strong> — ARPABET and IPA per token from the hybrid G2P.</li>
                  <li><strong>Prosody</strong> — raw pitch/energy curves and total duration.</li>
                  <li><strong>SSML AST</strong> — parsed SSML tree (only present when the input contained SSML).</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Zap className="h-4 w-4 text-primary" /> Performance tips
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-muted-foreground">
                <ul className="list-disc space-y-1 pl-5">
                  <li>Acoustic backends are now cached per-process — second and later requests skip model loading entirely.</li>
                  <li>The API warms up the default tier on startup, so the first user request is fast too.</li>
                  <li>Identical synth requests are deduplicated through the on-disk audio cache.</li>
                  <li>Stick to the Draft tier (Piper) when you only need a quick preview — it's the fastest backend.</li>
                  <li>Use Studio (Qwen3) only for final renders; it ships higher quality at the cost of more compute.</li>
                </ul>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-base">
                <HelpCircle className="h-4 w-4 text-primary" /> Troubleshooting
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-2 md:grid-cols-2">
              {troubleshooting.map((item) => (
                <div key={item.title} className="rounded-md border bg-muted/20 p-3 text-sm">
                  <div className="font-medium text-foreground">{item.title}</div>
                  <div className="text-muted-foreground">{item.detail}</div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-base"><ShieldCheck className="h-4 w-4 text-primary" /> UX Safety Rules</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-2 sm:grid-cols-2">
              {behaviorRules.map((item) => (
                <div key={item} className="rounded-md border bg-muted/20 p-3 text-sm text-muted-foreground">
                  {item}
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
