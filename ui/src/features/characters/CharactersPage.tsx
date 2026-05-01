import { useDeferredValue, useMemo, useRef, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Globe2, Search, Sparkles, CheckCircle2, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { useVoiceCharactersQuery, useCapabilitiesQuery, useHealthQuery } from '@/hooks/queries';
import { synthesize, listVoiceCategories } from '@/api/endpoints';
import { useStudioStore } from '@/stores/studio';
import { cn } from '@/lib/utils';
import { isBackendReady } from '@/lib/backend-status';
import { BackendStatusNotice } from '@/components/common/BackendStatusNotice';
import { HelpHint } from '@/components/common/HelpHint';
import { LicenseBadge } from './LicenseBadge';

interface CategoryInfo {
  id: string;
  label: string;
}

const PREVIEW_TEXT =
  'Hi, this is a quick sample of how this character sounds in TTS Studio.';

export function CharactersPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const audioRef = useRef<HTMLAudioElement>(null);
  const previewUrlRef = useRef<string | null>(null);

  const [q, setQ] = useState('');
  const [language, setLanguage] = useState<string>('all');
  const [gender, setGender] = useState<'all' | 'female' | 'male'>('all');
  const [category, setCategory] = useState<string>('all');
  const [page, setPage] = useState(0);
  const [previewing, setPreviewing] = useState<string | null>(null);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [categories, setCategories] = useState<CategoryInfo[]>([]);

  const deferredQ = useDeferredValue(q);
  const limit = 60;

  const health = useHealthQuery();
  const backendReady = isBackendReady(health.data?.status);
  const caps = useCapabilitiesQuery();

  const setCharacter = useStudioStore((s) => s.setVoiceCharacter);
  const setTier = useStudioStore((s) => s.setTier);
  const currentCharacter = useStudioStore((s) => s.voiceCharacter);

  const query = useMemo(
    () => ({
      q: deferredQ.trim() || undefined,
      language: language !== 'all' ? language : undefined,
      gender: gender !== 'all' ? gender : undefined,
      category: category !== 'all' ? category : undefined,
      limit,
      offset: page * limit,
    }),
    [deferredQ, language, gender, category, page],
  );

  const { data, isLoading, isFetching } = useVoiceCharactersQuery(query, backendReady);

  // Reset page when filters change
  useEffect(() => {
    setPage(0);
  }, [deferredQ, language, gender, category]);

  // Load category list once
  useEffect(() => {
    listVoiceCategories()
      .then((rows) => setCategories(rows.map((r) => ({ id: r.id, label: r.label }))))
      .catch(() => undefined);
  }, []);

  useEffect(() => () => {
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
      previewUrlRef.current = null;
    }
  }, []);

  const languageOptions = useMemo(() => {
    const set = new Set<string>();
    (data?.items ?? []).forEach((c) => set.add(c.language));
    return Array.from(set).sort();
  }, [data]);

  const stopPreview = () => {
    if (!audioRef.current) return;
    audioRef.current.pause();
    audioRef.current.currentTime = 0;
    audioRef.current.removeAttribute('src');
    audioRef.current.load();
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
      previewUrlRef.current = null;
    }
    setPreviewing(null);
  };

  const previewCharacter = async (id: string) => {
    if (previewing === id) {
      stopPreview();
      return;
    }
    try {
      setLoadingId(id);
      const { blob } = await synthesize({
        text: PREVIEW_TEXT,
        format: 'wav',
        tier: 'studio',
        speed: 1,
        pitch: 0,
        volume: 1,
        ssml: false,
        voice_character: id,
      });
      if (!audioRef.current) return;
      audioRef.current.pause();
      audioRef.current.removeAttribute('src');
      audioRef.current.load();
      if (previewUrlRef.current) {
        URL.revokeObjectURL(previewUrlRef.current);
        previewUrlRef.current = null;
      }
      const url = URL.createObjectURL(blob);
      previewUrlRef.current = url;
      audioRef.current.src = url;
      await audioRef.current.play();
      setPreviewing(id);
    } catch (error) {
      stopPreview();
      const message = error instanceof Error ? error.message : 'Could not preview this character.';
      toast.error(message);
      setPreviewing(null);
    } finally {
      setLoadingId(null);
    }
  };

  const pickForStudio = (id: string) => {
    setCharacter(id);
    setTier('studio');
    toast.success(t('characters.applied', { defaultValue: 'Character applied to Studio.' }));
    navigate('/');
  };

  const total = data?.total ?? 0;
  const pageCount = Math.max(1, Math.ceil(total / limit));
  const subtitle = backendReady
    ? t('characters.subtitle', {
        defaultValue: '{{count}} distinct Qwen3 originals · no duplicate speaker aliases',
        count: caps.data?.voice_characters_total ?? total,
      })
    : t('characters.subtitleOffline', {
        defaultValue: 'Distinct Qwen3 originals load when the backend is online.',
      });

  return (
    <div className="container mx-auto max-w-7xl space-y-6 p-6">
      <audio
        ref={audioRef}
        onEnded={stopPreview}
        controlsList="nodownload noremoteplayback"
        preload="none"
        className="hidden"
      />

      <header className="flex items-start justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
            <Globe2 className="h-6 w-6 text-primary" />
            {t('characters.title', { defaultValue: 'Voice characters' })}
            <HelpHint text="Pick from the real Qwen3 speaker originals, each with distinct speaker, language, category, style and emotion metadata. Selecting a character fills Studio controls in one click; you can still tweak them." />
          </h1>
          <p className="text-sm text-muted-foreground">
            {subtitle}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="outline" onClick={() => navigate('/voice-lab')}>
            {t('voices.createVoice', { defaultValue: 'Create custom voice' })}
          </Button>
          <Button variant="outline" onClick={() => navigate('/compare')}>
            {t('characters.compare', { defaultValue: 'A/B compare' })}
          </Button>
        </div>
      </header>

      {!backendReady && <BackendStatusNotice message="Voice characters need the backend online." />}

      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={t('characters.search', { defaultValue: 'Search by name, region or persona…' })}
            className="ps-9"
          />
        </div>
        <Select value={language} onValueChange={setLanguage}>
          <SelectTrigger className="w-44"><SelectValue placeholder="Language" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All languages</SelectItem>
            {languageOptions.map((code) => (
              <SelectItem key={code} value={code}>{code}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={gender} onValueChange={(v) => setGender(v as typeof gender)}>
          <SelectTrigger className="w-36"><SelectValue placeholder="Gender" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All genders</SelectItem>
            <SelectItem value="female">Female</SelectItem>
            <SelectItem value="male">Male</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Category tabs */}
      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          size="sm"
          variant={category === 'all' ? 'gradient' : 'outline'}
          onClick={() => setCategory('all')}
        >All</Button>
        {categories.map((c) => (
          <Button
            key={c.id}
            type="button"
            size="sm"
            variant={category === c.id ? 'gradient' : 'outline'}
            onClick={() => setCategory(c.id)}
          >{c.label}</Button>
        ))}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 12 }).map((_, i) => <Skeleton key={i} className="h-44" />)}
        </div>
      ) : !data || data.items.length === 0 ? (
        <div className="flex h-60 items-center justify-center rounded-lg border-2 border-dashed text-sm text-muted-foreground">
          No characters match these filters.
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {data.items.map((c) => (
              <Card
                key={c.id}
                className={cn(
                  'group transition-colors hover:bg-accent/30',
                  currentCharacter === c.id && 'border-primary ring-2 ring-primary/25',
                )}
              >
                <CardContent className="p-5">
                  <div className="flex items-start justify-between">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg border bg-primary/10">
                      <Sparkles className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex items-center gap-1">
                      <Badge variant="info">{c.persona_label}</Badge>
                      {currentCharacter === c.id && (
                        <CheckCircle2 className="h-4 w-4 text-primary" aria-label="Selected" />
                      )}
                    </div>
                  </div>
                  <div className="mt-3 space-y-1">
                    <div className="font-semibold leading-tight">{c.name}</div>
                    {c.tagline && (
                      <div className="text-xs font-medium text-foreground/80">{c.tagline}</div>
                    )}
                    <div className="flex flex-wrap items-center gap-1 text-xs text-muted-foreground">
                      <Badge variant="outline" className="h-5 px-1.5 text-[10px]">{c.accent}</Badge>
                      <Badge variant="outline" className="h-5 px-1.5 text-[10px]">{c.gender}</Badge>
                      <Badge variant="outline" className="h-5 px-1.5 text-[10px]">{c.age_range}</Badge>
                      <Badge variant="outline" className="h-5 px-1.5 text-[10px]">{c.default_emotion}</Badge>
                      {c.source_type === 'qwen_clone' && (
                        <Badge variant="info" className="h-5 px-1.5 text-[10px]">cloned</Badge>
                      )}
                      <LicenseBadge
                        license={c.license ?? 'synthetic_only'}
                        attributionRequired={c.attribution_required}
                        attributionString={c.attribution_string}
                      />
                    </div>
                  </div>
                  <p className="mt-2 line-clamp-3 text-xs text-muted-foreground">{c.style_prompt}</p>
                  {c.inspiration_note && (
                    <p className="mt-1 text-[11px] italic text-muted-foreground/80">{c.inspiration_note}</p>
                  )}
                  <div className="mt-3 flex gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant={previewing === c.id ? 'secondary' : 'ghost'}
                      className="flex-1"
                      disabled={!backendReady || (loadingId !== null && loadingId !== c.id)}
                      onClick={() => void previewCharacter(c.id)}
                    >
                      {loadingId === c.id ? (
                        <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Synthesizing…</>
                      ) : previewing === c.id ? (
                        'Stop'
                      ) : (
                        'Preview'
                      )}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant={currentCharacter === c.id ? 'secondary' : 'gradient'}
                      className="flex-1"
                      onClick={() => pickForStudio(c.id)}
                    >
                      {currentCharacter === c.id ? 'In use' : 'Use'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="flex items-center justify-between pt-2 text-sm text-muted-foreground">
            <span>
              {isFetching ? <Loader2 className="inline h-3 w-3 animate-spin" /> : null}{' '}
              Page {page + 1} of {pageCount} · {total} matches
            </span>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
              >Previous</Button>
              <Button
                size="sm"
                variant="outline"
                disabled={page + 1 >= pageCount}
                onClick={() => setPage((p) => p + 1)}
              >Next</Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
