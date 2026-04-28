import { useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CheckCircle2, Mic, Search, Sparkles } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { useHealthQuery, useVoicesQuery } from '@/hooks/queries';
import { useStudioStore } from '@/stores/studio';
import { useNavigate } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { isBackendReady } from '@/lib/backend-status';
import { synthesize } from '@/api/endpoints';
import { BackendStatusNotice } from '@/components/common/BackendStatusNotice';
import { HelpHint } from '@/components/common/HelpHint';
import { SampleTextPicker } from '@/components/common/SampleTextPicker';
import { toast } from 'sonner';

export function VoicesPage() {
  const { t } = useTranslation();
  const { data, isLoading } = useVoicesQuery();
  const health = useHealthQuery();
  const setVoice = useStudioStore((s) => s.setVoice);
  const currentVoice = useStudioStore((s) => s.voiceId);
  const navigate = useNavigate();
  const previewAudioRef = useRef<HTMLAudioElement>(null);
  const backendReady = isBackendReady(health.data?.status);

  const [q, setQ] = useState('');
  const [gender, setGender] = useState<'all' | 'male' | 'female' | 'neutral'>('all');
  const [backend, setBackend] = useState<string>('all');
  const [previewLoadingId, setPreviewLoadingId] = useState<string | null>(null);
  const [previewingId, setPreviewingId] = useState<string | null>(null);

  const [previewText, setPreviewText] = useState(
    'Hello, this is a quick sample of this voice in TTS Studio.',
  );

  const filtered = useMemo(() => {
    return (data ?? []).filter((v) => {
      if (q && !v.name.toLowerCase().includes(q.toLowerCase())) return false;
      if (gender !== 'all' && v.gender !== gender) return false;
      if (backend !== 'all' && v.backend !== backend) return false;
      return true;
    });
  }, [data, q, gender, backend]);

  const backends = useMemo(() => {
    const set = new Set((data ?? []).map((v) => v.backend));
    return ['all', ...Array.from(set)];
  }, [data]);

  useEffect(() => {
    const audioEl = previewAudioRef.current;
    return () => {
      if (audioEl) {
        audioEl.pause();
        audioEl.removeAttribute('src');
        audioEl.load();
      }
    };
  }, []);

  const stopPreview = () => {
    if (!previewAudioRef.current) return;
    previewAudioRef.current.pause();
    previewAudioRef.current.currentTime = 0;
    setPreviewingId(null);
  };

  const previewVoice = async (voiceId: string) => {
    if (previewingId === voiceId) {
      stopPreview();
      return;
    }

    try {
      setPreviewLoadingId(voiceId);
      const { blob } = await synthesize({
        text: previewText,
        voice_id: voiceId,
        format: 'wav',
        tier: 'standard',
        speed: 1,
        pitch: 0,
        volume: 1,
        ssml: false,
      });

      if (!previewAudioRef.current) return;
      if (previewAudioRef.current) {
        previewAudioRef.current.pause();
        previewAudioRef.current.removeAttribute('src');
        previewAudioRef.current.load();
      }

      const dataUrl = await blobToDataUrl(blob);
      previewAudioRef.current.src = dataUrl;
      await previewAudioRef.current.play();
      setPreviewingId(voiceId);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Could not preview this voice.';
      toast.error(message);
      setPreviewingId(null);
    } finally {
      setPreviewLoadingId(null);
    }
  };

  return (
    <div className="container mx-auto max-w-7xl space-y-6 p-6">
      <audio
        ref={previewAudioRef}
        onEnded={() => setPreviewingId(null)}
        onPause={() => setPreviewingId((prev) => (prev ? null : prev))}
        controlsList="nodownload noremoteplayback"
        preload="none"
        className="hidden"
      />
      <header className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
            {t('voices.title')}
            <HelpHint text="Browse all available built-in voices and your own custom voices. Click Preview to play a short sample, or Use voice to load it into Studio." />
          </h1>
          <p className="text-sm text-muted-foreground">{t('voices.availableCount', { count: (data ?? []).length })}</p>
        </div>
        <Button variant="gradient" onClick={() => navigate('/voice-lab')}>
          <Mic className="h-4 w-4" /> {t('voices.createVoice')}
        </Button>
      </header>

      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={t('voices.search')}
            className="ps-9"
          />
        </div>
        <Select value={gender} onValueChange={(v) => setGender(v as typeof gender)}>
          <SelectTrigger className="w-36"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t('voices.filters.allGenders')}</SelectItem>
            <SelectItem value="female">{t('voices.filters.female')}</SelectItem>
            <SelectItem value="male">{t('voices.filters.male')}</SelectItem>
            <SelectItem value="neutral">{t('voices.filters.neutral')}</SelectItem>
          </SelectContent>
        </Select>
        <Select value={backend} onValueChange={setBackend}>
          <SelectTrigger className="w-36"><SelectValue /></SelectTrigger>
          <SelectContent>
            {backends.map((b) => (
              <SelectItem key={b} value={b}>{b === 'all' ? t('voices.filters.allBackends') : b}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <SampleTextPicker
        label="Preview text"
        onPick={(s) => setPreviewText(s.text)}
        disabled={previewLoadingId !== null}
      />

      {!backendReady && (
        <BackendStatusNotice message={t('voices.backendOfflinePreviewMessage')} />
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-40" />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex h-60 items-center justify-center rounded-lg border-2 border-dashed text-sm text-muted-foreground">
          {t('voices.empty')}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((v) => (
            <Card
              key={v.id}
              className={cn(
                'group cursor-pointer transition-colors hover:bg-accent/30',
                currentVoice === v.id && 'border-primary ring-2 ring-primary/25',
              )}
              onClick={() => setVoice(v.id)}
            >
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg border bg-primary/10">
                    <Sparkles className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex items-center gap-1">
                    {v.custom && <Badge variant="info">{t('voices.custom')}</Badge>}
                    {currentVoice === v.id && <CheckCircle2 className="h-4 w-4 text-primary" aria-label="Selected" />}
                  </div>
                </div>
                <div className="mt-3 space-y-1">
                  <div className="font-semibold">{v.name}</div>
                  <div className="flex flex-wrap gap-1 text-xs text-muted-foreground">
                    <span>{v.gender ?? '—'}</span>
                    <span>·</span>
                    <span>{v.language}</span>
                    <span>·</span>
                    <Badge variant="outline" className="h-5 px-1.5 text-[10px]">{v.backend}</Badge>
                  </div>
                </div>
                {v.description && (
                  <p className="mt-2 line-clamp-2 text-xs text-muted-foreground">{v.description}</p>
                )}
                <div className="mt-3 flex flex-wrap gap-1">
                  {v.tags.slice(0, 3).map((tag) => (
                    <Badge key={tag} variant="outline" className="text-[10px]">{tag}</Badge>
                  ))}
                </div>
                <Button
                  type="button"
                  size="sm"
                  variant={previewingId === v.id ? 'secondary' : 'ghost'}
                  className="mt-2 w-full"
                  disabled={!backendReady || (previewLoadingId !== null && previewLoadingId !== v.id)}
                  onClick={(event) => {
                    event.stopPropagation();
                    void previewVoice(v.id);
                  }}
                >
                  {previewLoadingId === v.id ? t('voices.previewLoading') : previewingId === v.id ? t('voices.previewStop') : t('voices.preview')}
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant={currentVoice === v.id ? 'secondary' : 'outline'}
                  className="mt-2 w-full"
                  onClick={(event) => {
                    event.stopPropagation();
                    setVoice(v.id);
                    navigate('/');
                  }}
                >
                  {currentVoice === v.id ? t('voices.selected') : t('voices.useVoice')}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

async function blobToDataUrl(blob: Blob): Promise<string> {
  return await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result ?? ''));
    reader.onerror = () => reject(new Error('Could not read audio blob.'));
    reader.readAsDataURL(blob);
  });
}
