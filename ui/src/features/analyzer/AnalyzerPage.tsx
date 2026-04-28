import { useState } from 'react';
import { useAnalyzeQuery } from '@/hooks/queries';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { HelpHint } from '@/components/common/HelpHint';
import { Copy, Loader2, ScanText } from 'lucide-react';
import { toast } from 'sonner';
import { SampleTextPicker } from '@/components/common/SampleTextPicker';

export function AnalyzerPage() {
  const [text, setText] = useState('Hello world. This is a test of the text-to-speech analyzer.');
  const [submitted, setSubmitted] = useState(text);
  const { data, isLoading, error } = useAnalyzeQuery(submitted, !!submitted);

  const copyJson = async (value: unknown) => {
    await navigator.clipboard.writeText(JSON.stringify(value ?? {}, null, 2));
    toast.success('Copied JSON');
  };

  return (
    <div className="container mx-auto max-w-6xl space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold tracking-tight">NLP Analyzer</h1>
        <p className="text-sm text-muted-foreground">Inspect tokens, phonemes, prosody, and the SSML AST.</p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Input
            <HelpHint text="Paste plain text or SSML markup. The analyzer runs the same NLP pipeline used by synthesis (normalize → segment → analyze → G2P → prosody) and returns its intermediate state for inspection." />
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <SampleTextPicker onPick={(s) => setText(s.text)} disabled={isLoading} />
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Text to analyze…"
            className="min-h-[120px] font-mono text-sm"
          />
          <Button variant="gradient" onClick={() => setSubmitted(text)} disabled={!text.trim()}>
            <ScanText className="h-4 w-4" /> Analyze
          </Button>
        </CardContent>
      </Card>

      {isLoading && (
        <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Analyzing…
        </div>
      )}
      {error && <div className="rounded-md border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">{(error as { message?: string }).message}</div>}

      {data && (
        <Tabs defaultValue="tokens">
          <TabsList>
            <TabsTrigger value="tokens">Tokens</TabsTrigger>
            <TabsTrigger value="phonemes">Phonemes</TabsTrigger>
            <TabsTrigger value="prosody">Prosody</TabsTrigger>
            <TabsTrigger value="ssml">SSML AST</TabsTrigger>
          </TabsList>

          <TabsContent value="tokens">
            <Card>
              <CardContent className="overflow-x-auto p-4">
                <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
                  Word-level tokens with linguistic type and stress markers.
                  <HelpHint text="Each token comes from spaCy with stress assignments from the G2P stage. Punctuation is tagged 'punct'." />
                </div>
                <table className="w-full min-w-[560px] text-sm" aria-label="Analyzer tokens">
                  <thead className="border-b text-xs text-muted-foreground">
                    <tr><th className="p-2 text-start">Token</th><th className="p-2 text-start">Type</th><th className="p-2 text-start">Stress</th></tr>
                  </thead>
                  <tbody>
                    {data.tokens.map((tok, i) => (
                      <tr key={i} className="border-b">
                        <td className="p-2 font-mono">{tok.text}</td>
                        <td className="p-2"><Badge variant="outline">{tok.type}</Badge></td>
                        <td className="p-2 font-mono text-xs">{tok.stress?.join(' ')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="phonemes">
            <Card>
              <CardContent className="space-y-2 p-4 text-sm">
                {data.tokens.map((tok, i) => (
                  <div key={i} className="flex flex-wrap items-center gap-2 border-b py-1">
                    <span className="font-mono w-24">{tok.text}</span>
                    <span className="font-mono text-xs text-muted-foreground">ARPABET: {tok.phonemes_arpabet?.join(' ') ?? '—'}</span>
                    <span className="font-mono text-xs text-info">IPA: {tok.phonemes_ipa ?? '—'}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="prosody">
            <Card>
              <CardContent className="space-y-3 p-4">
                <Button size="sm" variant="outline" onClick={() => void copyJson(data.prosody ?? {})}>
                  <Copy className="h-4 w-4" /> Copy JSON
                </Button>
                <pre className="overflow-x-auto rounded-md bg-muted p-3 text-xs">
                  {JSON.stringify(data.prosody ?? {}, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ssml">
            <Card>
              <CardContent className="space-y-3 p-4">
                <Button size="sm" variant="outline" onClick={() => void copyJson(data.ssml_ast ?? {})}>
                  <Copy className="h-4 w-4" /> Copy JSON
                </Button>
                <pre className="overflow-x-auto rounded-md bg-muted p-3 text-xs">
                  {JSON.stringify(data.ssml_ast ?? {}, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
