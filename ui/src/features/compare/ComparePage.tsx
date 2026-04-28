import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Loader2, Plus, Play, X, Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useVoiceCharactersQuery, useHealthQuery } from '@/hooks/queries';
import { synthesize } from '@/api/endpoints';
import { isBackendReady } from '@/lib/backend-status';
import { BackendStatusNotice } from '@/components/common/BackendStatusNotice';
import { LicenseBadge } from '@/features/characters/LicenseBadge';
import { SampleTextPicker } from '@/components/common/SampleTextPicker';

const DEFAULT_TEXT =
  'The quick brown fox jumps over the lazy dog. I will tell you a story you have never heard before.';

interface Slot {
  voiceId: string | null;
  url: string | null;
  loading: boolean;
}

const MAX_SLOTS = 4;

export function ComparePage() {
  const { t } = useTranslation();
  const health = useHealthQuery();
  const backendReady = isBackendReady(health.data?.status);
  const { data } = useVoiceCharactersQuery({ limit: 200 }, backendReady);
  const allVoices = useMemo(() => data?.items ?? [], [data]);
  const voiceById = useMemo(() => Object.fromEntries(allVoices.map((v) => [v.id, v])), [allVoices]);

  const [text, setText] = useState(DEFAULT_TEXT);
  const [slots, setSlots] = useState<Slot[]>([
    { voiceId: null, url: null, loading: false },
    { voiceId: null, url: null, loading: false },
  ]);

  // Revoke object URLs on unmount.
  useEffect(() => () => slots.forEach((s) => { if (s?.url) URL.revokeObjectURL(s.url); }), [slots]);

  const updateSlot = (i: number, patch: Partial<Slot>) =>
    setSlots((curr) => curr.map((s, idx) => (idx === i ? { ...s, ...patch } : s)));

  const removeSlot = (i: number) => {
    setSlots((curr) => {
      const s = curr[i];
      if (s?.url) URL.revokeObjectURL(s.url);
      return curr.filter((_, idx) => idx !== i);
    });
  };

  const addSlot = () => {
    if (slots.length >= MAX_SLOTS) return;
    setSlots((curr) => [...curr, { voiceId: null, url: null, loading: false }]);
  };

  const renderSlot = async (i: number) => {
    const slot = slots[i];
    if (!slot || !slot.voiceId) {
      toast.error('Pick a voice for this slot first.');
      return;
    }
    if (!text.trim()) {
      toast.error('Type the text to compare.');
      return;
    }
    if (slot.url) URL.revokeObjectURL(slot.url);
    updateSlot(i, { loading: true, url: null });
    try {
      const { blob } = await synthesize({
        text,
        format: 'wav',
        tier: 'studio',
        speed: 1,
        pitch: 0,
        volume: 1,
        ssml: false,
        voice_character: slot.voiceId,
      });
      updateSlot(i, { loading: false, url: URL.createObjectURL(blob) });
    } catch (err) {
      updateSlot(i, { loading: false, url: null });
      toast.error(err instanceof Error ? err.message : 'Synthesis failed.');
    }
  };

  const renderAll = async () => {
    for (let i = 0; i < slots.length; i++) {
      // sequential so the GPU is not flooded
      await renderSlot(i);
    }
  };

  return (
    <div className="container mx-auto max-w-7xl space-y-6 p-6">
      <header>
        <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
          <Sparkles className="h-6 w-6 text-primary" />
          {t('compare.title', { defaultValue: 'A/B voice comparison' })}
        </h1>
        <p className="text-sm text-muted-foreground">
          {t('compare.subtitle', {
            defaultValue: 'Render the same line through multiple voices side-by-side to verify they really sound different.',
          })}
        </p>
      </header>

      {!backendReady && <BackendStatusNotice message="A/B comparison needs the backend online." />}

      <Card>
        <CardContent className="space-y-3 p-4">
          <SampleTextPicker onPick={(s) => setText(s.text)} />
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Text to render…"
            className="min-h-[110px]"
          />
          <div className="flex justify-end gap-2">
            <Button variant="outline" size="sm" onClick={addSlot} disabled={slots.length >= MAX_SLOTS}>
              <Plus className="me-1 h-4 w-4" /> Add slot
            </Button>
            <Button variant="gradient" size="sm" onClick={() => void renderAll()} disabled={!backendReady}>
              <Play className="me-1 h-4 w-4" /> Render all
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {slots.map((slot, i) => {
          const v = slot.voiceId ? voiceById[slot.voiceId] : undefined;
          return (
            <Card key={i}>
              <CardContent className="space-y-3 p-4">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-semibold text-muted-foreground">Slot {i + 1}</span>
                  {slots.length > 1 && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={() => removeSlot(i)}
                      aria-label="Remove slot"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
                <Select
                  value={slot.voiceId ?? ''}
                  onValueChange={(value) => updateSlot(i, { voiceId: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Pick a voice…" />
                  </SelectTrigger>
                  <SelectContent className="max-h-80">
                    {allVoices.map((vo) => (
                      <SelectItem key={vo.id} value={vo.id}>
                        {vo.name} · {vo.accent}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {v && (
                  <div className="space-y-1">
                    <div className="text-sm font-semibold leading-tight">{v.name}</div>
                    {v.tagline && <div className="text-xs text-muted-foreground">{v.tagline}</div>}
                    <div className="flex flex-wrap gap-1">
                      <Badge variant="outline" className="h-5 px-1.5 text-[10px]">{v.gender}</Badge>
                      <Badge variant="outline" className="h-5 px-1.5 text-[10px]">{v.age_range}</Badge>
                      <Badge variant="outline" className="h-5 px-1.5 text-[10px]">{v.default_emotion}</Badge>
                      <LicenseBadge
                        license={v.license ?? 'synthetic_only'}
                        attributionRequired={v.attribution_required}
                        attributionString={v.attribution_string}
                      />
                    </div>
                  </div>
                )}

                <Button
                  size="sm"
                  variant="secondary"
                  className="w-full"
                  disabled={!backendReady || !slot.voiceId || slot.loading}
                  onClick={() => void renderSlot(i)}
                >
                  {slot.loading ? <Loader2 className="me-1 h-3.5 w-3.5 animate-spin" /> : <Play className="me-1 h-3.5 w-3.5" />}
                  {slot.loading ? 'Synthesizing…' : 'Render slot'}
                </Button>

                {slot.url && (
                  <audio controls className="w-full" src={slot.url} preload="metadata" />
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
