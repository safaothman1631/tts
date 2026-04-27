import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { GitBranch } from 'lucide-react';

interface Stage {
  id: string;
  name: string;
  description: string;
}

const STAGES: Stage[] = [
  { id: 'ssml', name: 'SSML Parser', description: 'Parses inbound SSML into an internal AST.' },
  { id: 'norm', name: 'Text Normalizer', description: 'Numbers, dates, currencies, abbreviations.' },
  { id: 'ling', name: 'Linguistic', description: 'Tokenization, POS tagging.' },
  { id: 'g2p', name: 'G2P', description: 'Grapheme to phoneme conversion (CMUDict + neural fallback).' },
  { id: 'homo', name: 'Homograph', description: 'Disambiguates context-sensitive words.' },
  { id: 'pros', name: 'Prosody', description: 'Pitch, energy, and duration prediction.' },
  { id: 'ac', name: 'Acoustic Model', description: 'Piper ONNX by default, with VITS/XTTS options and SAPI fallback.' },
  { id: 'voc', name: 'Vocoder', description: 'Passthrough for end-to-end waveforms; vocoder stage remains available for mel backends.' },
  { id: 'post', name: 'Post-processing', description: 'Loudness, denoise, format encode.' },
];

export function PipelinePage() {
  return (
    <div className="container mx-auto max-w-5xl space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold tracking-tight">Pipeline Visualizer</h1>
        <p className="text-sm text-muted-foreground">A tour through every stage of the eng-tts pipeline.</p>
      </header>

      <div className="space-y-3">
        {STAGES.map((s, i) => (
          <Card key={s.id} className="transition-colors hover:bg-accent/30">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-3 text-base">
                <span className="flex h-7 w-7 items-center justify-center rounded-md bg-gradient-to-br from-primary/40 to-info/30 text-xs font-bold text-primary">
                  {i + 1}
                </span>
                {s.name}
                {s.id === 'ac' && <Badge variant="info" className="ms-1">Piper ready</Badge>}
                {i < STAGES.length - 1 && <GitBranch className="ms-auto h-4 w-4 text-muted-foreground" />}
              </CardTitle>
              <CardDescription>{s.description}</CardDescription>
            </CardHeader>
            <CardContent />
          </Card>
        ))}
      </div>
    </div>
  );
}
