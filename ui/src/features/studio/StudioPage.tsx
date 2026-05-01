import { useTranslation } from 'react-i18next';
import { Sparkles, Loader2, Download, Radio, ArrowLeftRight, X, Plus, Trash2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { useStudioStore } from '@/stores/studio';
import { useCapabilitiesQuery, useHealthQuery, useVoicesQuery } from '@/hooks/queries';
import { useSynthesize } from '@/hooks/useSynthesize';
import { AudioPlayer } from '@/components/audio/AudioPlayer';
import { BackendStatusNotice } from '@/components/common/BackendStatusNotice';
import { HelpHint } from '@/components/common/HelpHint';
import { audioExtensionFromBlob, downloadBlob } from '@/lib/utils';
import { isBackendReady } from '@/lib/backend-status';
import { useState } from 'react';
import type { SynthSegment, Voice } from '@/types/api';
import { SampleTextPicker } from '@/components/common/SampleTextPicker';

const DEFAULT_VOICE_VALUE = '__default_voice__';
const INHERIT_VOICE_VALUE = '__inherit_voice__';
const NONE_VALUE = '__none__';

const LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'ckb', label: 'کوردی' },
  { value: 'ar', label: 'العربية' },
  { value: 'tr', label: 'Türkçe' },
  { value: 'zh', label: '中文' },
  { value: 'ja', label: '日本語' },
  { value: 'ko', label: '한국어' },
  { value: 'de', label: 'Deutsch' },
  { value: 'fr', label: 'Français' },
  { value: 'es', label: 'Español' },
  { value: 'it', label: 'Italiano' },
  { value: 'pt', label: 'Português' },
  { value: 'ru', label: 'Русский' },
];

function formatSpeakerLabel(value: string): string {
  return value
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

export function StudioPage() {
  const { t } = useTranslation();
  const studio = useStudioStore();
  const voices = useVoicesQuery();
  const health = useHealthQuery();
  const capabilities = useCapabilitiesQuery();
  const synth = useSynthesize();
  const [useStream, setUseStream] = useState(false);
  const backendReady = isBackendReady(health.data?.status);
  const supportsSegments = capabilities.isLoading || !!capabilities.data?.endpoints.includes('/v1/synthesize/segments.wav');
  const supportsStreaming = !!capabilities.data?.streaming && !studio.segmentsMode;
  const supportsStylePrompt = capabilities.isLoading || !!capabilities.data?.controls.includes('style_prompt');
  const supportsPause = capabilities.isLoading || !!capabilities.data?.controls.includes('pause_after_ms');
  const activeText = studio.segmentsMode
    ? studio.segments.map((segment) => segment.text).join('\n\n')
    : studio.text;
  const canSynthesize = backendReady
    && !synth.isPending
    && activeText.trim().length > 0
    && (!studio.segmentsMode || supportsSegments);

  const charCount = activeText.length;
  const estSeconds = Math.max(1, Math.round((activeText.split(/\s+/).filter(Boolean).length / 150) * 60 / studio.speed));

  const onSynth = async () => {
    try {
      await synth.mutateAsync({ stream: useStream && !studio.segmentsMode, keepPrevious: !!studio.currentAudioUrl });
    } catch {
      // Error toast is handled centrally in useSynthesize.onError.
    }
  };

  const onDownload = async () => {
    const audioUrl = studio.currentAudioUrl;
    if (!audioUrl && !studio.currentAudioBlob) return;
    if (studio.currentAudioBlob) {
      const ext = audioExtensionFromBlob(studio.currentAudioBlob, studio.format);
      downloadBlob(studio.currentAudioBlob, `tts-${Date.now()}.${ext}`);
      return;
    }
    if (!audioUrl) return;
    const res = await fetch(audioUrl);
    const blob = await res.blob();
    const ext = audioExtensionFromBlob(blob, studio.format);
    downloadBlob(blob, `tts-${Date.now()}.${ext}`);
  };

  return (
    <div className="container mx-auto max-w-7xl space-y-6 p-6">
      <header className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight">
          <span className="gradient-text">{t('app.name')}</span>
        </h1>
        <p className="text-muted-foreground">{t('app.tagline')}</p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  Text
                </CardTitle>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="segments" className="flex items-center gap-1.5 text-xs">
                      {t('studio.segments')}
                      <HelpHint text="Split text into multiple paragraphs, each with its own voice, tier, speed and pause. Useful for dialogues and audiobooks." />
                    </Label>
                    <Switch
                      id="segments"
                      checked={studio.segmentsMode}
                      onCheckedChange={studio.setSegmentsMode}
                      disabled={!supportsSegments}
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label htmlFor="stream" className="flex items-center gap-1.5 text-xs">
                      Stream
                      <HelpHint text="Receive audio chunks as they are produced. First-byte latency is lower but file size is identical when finished." />
                    </Label>
                    <Switch id="stream" checked={useStream && supportsStreaming} onCheckedChange={setUseStream} disabled={!supportsStreaming} />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label htmlFor="ssml" className="flex items-center gap-1.5 text-xs">
                      {t('studio.ssml')}
                      <HelpHint text="Treat the input as Speech Synthesis Markup Language. Use <break>, <emphasis>, <prosody> tags for fine control." />
                    </Label>
                    <Switch id="ssml" checked={studio.ssmlMode && !studio.segmentsMode} onCheckedChange={studio.setSsmlMode} disabled={studio.segmentsMode} />
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {studio.segmentsMode ? (
                <SegmentEditor
                  segments={studio.segments}
                  voices={voices.data ?? []}
                  supportsPause={supportsPause}
                  supportsStylePrompt={supportsStylePrompt}
                  onAdd={studio.addSegment}
                  onRemove={studio.removeSegment}
                  onUpdate={studio.updateSegment}
                />
              ) : (
                <>
                  <SampleTextPicker
                    onPick={(s) => studio.setText(s.text)}
                    disabled={synth.isPending}
                  />
                  <Textarea
                    value={studio.text}
                    onChange={(e) => studio.setText(e.target.value)}
                    placeholder={t('studio.placeholder')}
                    className="min-h-[280px] font-mono text-sm"
                    aria-label="TTS input"
                  />
                </>
              )}
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground">
                <div className="flex gap-2">
                  <Badge variant="outline">{t('studio.characters', { count: charCount })}</Badge>
                  <Badge variant="outline">{t('studio.estimated', { seconds: estSeconds })}</Badge>
                </div>
                <Button
                  type="button"
                  size="lg"
                  variant="gradient"
                  onClick={onSynth}
                  disabled={!canSynthesize}
                  className="min-w-[160px]"
                >
                  {synth.isPending ? (
                    <><Loader2 className="h-4 w-4 animate-spin" /> {t('studio.synthesizing')}</>
                  ) : (
                    <><Sparkles className="h-4 w-4" /> {t('actions.synthesize')}</>
                  )}
                </Button>
              </div>
              {!backendReady && (
                <BackendStatusNotice message={t('studio.backendOfflineMessage')} />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between gap-2">
                <CardTitle>Output</CardTitle>
                <div className="flex items-center gap-2">
                  {studio.compareUrl && (
                    <Button type="button" size="sm" variant="outline" onClick={studio.swapAB} title="Swap A/B">
                      <ArrowLeftRight className="h-4 w-4" /> A/B
                    </Button>
                  )}
                  {(studio.currentAudioUrl || studio.currentAudioBlob) && (
                    <Button type="button" size="sm" variant="ghost" onClick={onDownload}>
                      <Download className="h-4 w-4" /> {t('actions.download')}
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {studio.streamProgress !== undefined && (
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span className="flex items-center gap-1.5"><Radio className="h-3 w-3 animate-pulse" /> Streaming…</span>
                    <span className="font-mono tabular-nums">{Math.round(studio.streamProgress * 100)}%</span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full bg-gradient-to-r from-primary to-cyan-400 transition-[width] duration-200"
                      style={{ width: `${studio.streamProgress * 100}%` }}
                    />
                  </div>
                </div>
              )}
              {studio.currentAudioUrl || studio.currentAudioBlob ? (
                <AudioPlayer url={studio.currentAudioUrl} blob={studio.currentAudioBlob} format={studio.format} />
              ) : (
                <div className="flex h-32 items-center justify-center rounded-lg border-2 border-dashed text-sm text-muted-foreground">
                  {t('studio.noAudio')}
                </div>
              )}
              {studio.compareUrl && (
                <div className="rounded-lg border bg-muted/30 p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <Label className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                      B · {studio.compareLabel ?? 'Previous'}
                    </Label>
                    <Button type="button" size="icon" variant="ghost" className="h-6 w-6" onClick={() => studio.setCompare(undefined)}>
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                  <AudioPlayer url={studio.compareUrl} blob={studio.compareBlob} format={studio.format} />
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card className="h-fit lg:sticky lg:top-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Settings
              <HelpHint text="Voice, quality and prosody controls. Use the Studio tier to unlock Qwen3 features such as style prompts, speaker presets and emotion." />
            </CardTitle>
            <CardDescription>Voice & quality controls</CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <Field
              label={t('studio.voice')}
              hint="Pick a built-in or custom voice. Leave on Default to let the backend choose."
            >
              <Select
                value={studio.voiceId ?? DEFAULT_VOICE_VALUE}
                onValueChange={(value) => studio.setVoice(value === DEFAULT_VOICE_VALUE ? undefined : value)}
              >
                <SelectTrigger><SelectValue placeholder="Default voice" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value={DEFAULT_VOICE_VALUE}>{t('studio.defaultVoice')}</SelectItem>
                  {voices.isLoading && <div className="p-2 text-xs text-muted-foreground">{t('common.loading')}</div>}
                  {voices.data?.map((v) => (
                    <SelectItem key={v.id} value={v.id}>{v.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>

            <Field
              label={t('studio.tier')}
              hint="Draft = fastest (Piper). Standard = balanced (Piper). Studio = highest quality (Qwen3 with prompts and emotion)."
            >
              <Select value={studio.tier} onValueChange={(v) => studio.setTier(v as 'draft' | 'standard' | 'studio')}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="draft">{t('studio.tiers.draft')}</SelectItem>
                  <SelectItem value="standard">{t('studio.tiers.standard')}</SelectItem>
                  <SelectItem value="studio">{t('studio.tiers.studio')}</SelectItem>
                </SelectContent>
              </Select>
            </Field>

            <Field
              label={t('studio.format')}
              hint="Output container. WAV is uncompressed and lossless. Other formats may require backend support."
            >
              <Select value={studio.segmentsMode ? 'wav' : studio.format} onValueChange={(v) => studio.setFormat(v as 'wav' | 'mp3' | 'flac' | 'ogg')} disabled={studio.segmentsMode}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="wav">WAV</SelectItem>
                  <SelectItem value="mp3">MP3</SelectItem>
                  <SelectItem value="flac">FLAC</SelectItem>
                  <SelectItem value="ogg">OGG</SelectItem>
                </SelectContent>
              </Select>
            </Field>

            <Field
              label="Language"
              hint="Language hint for the acoustic model. Mostly relevant for Qwen3 (Studio tier) which supports many languages."
            >
              <Select
                value={studio.language ?? NONE_VALUE}
                onValueChange={(v) => studio.setLanguage(v === NONE_VALUE ? undefined : v)}
              >
                <SelectTrigger><SelectValue placeholder="Auto" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value={NONE_VALUE}>Auto</SelectItem>
                  {LANGUAGE_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>

            <Separator />

            <SliderField
              label={t('studio.speed')}
              hint="Playback rate multiplier. 1.00× keeps the voice natural; lower for slower, higher for faster delivery."
              value={studio.speed}
              min={0.5} max={2} step={0.05}
              format={(v) => `${v.toFixed(2)}×`}
              onChange={studio.setSpeed}
            />
            <SliderField
              label={t('studio.pitch')}
              hint="Pitch shift in semitones (±12). Positive values raise the perceived voice frequency."
              value={studio.pitch}
              min={-12} max={12} step={1}
              format={(v) => `${v > 0 ? '+' : ''}${v} st`}
              onChange={studio.setPitch}
            />
            <SliderField
              label={t('studio.volume')}
              hint="Output gain. 100% is unchanged; values above 100% can clip on quiet content."
              value={studio.volume}
              min={0} max={2} step={0.05}
              format={(v) => `${Math.round(v * 100)}%`}
              onChange={studio.setVolume}
            />

            {studio.voiceCharacter && (
              <div className="rounded-lg border border-primary/30 bg-primary/5 p-3 text-xs">
                <div className="mb-1 flex items-center justify-between">
                  <span className="font-medium text-foreground">Active character</span>
                  <button
                    type="button"
                    className="text-[11px] text-muted-foreground underline-offset-4 hover:underline"
                    onClick={() => studio.setVoiceCharacter(undefined)}
                  >
                    Clear
                  </button>
                </div>
                <code className="break-all text-[11px] text-muted-foreground">{studio.voiceCharacter}</code>
                <p className="mt-1 text-[11px] text-muted-foreground">
                  Speaker / language / style / emotion are auto-filled by the character. Anything you set here overrides them.
                </p>
              </div>
            )}

            {studio.tier === 'studio' && (
              <>
                <Separator />
                <Field
                  label="Style preset"
                  hint="Predefined Qwen3 narration styles. Selecting one fills the Style prompt below."
                >
                  <Select
                    value={NONE_VALUE}
                    onValueChange={(v) => {
                      const preset = (capabilities.data?.style_presets ?? []).find((p) => p.id === v);
                      if (preset) studio.setStylePrompt(preset.prompt);
                    }}
                  >
                    <SelectTrigger><SelectValue placeholder="Choose a preset…" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value={NONE_VALUE}>None</SelectItem>
                      {(capabilities.data?.style_presets ?? []).map((preset) => (
                        <SelectItem key={preset.id} value={preset.id}>{preset.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </Field>

                <Field
                  label={t('studio.stylePrompt')}
                  hint="Free-form description of how the voice should sound (e.g. 'warm storytelling, slow pacing'). Sent to Qwen3 as an instruction."
                >
                  <Input
                    value={studio.stylePrompt}
                    onChange={(e) => studio.setStylePrompt(e.target.value)}
                    placeholder={t('studio.stylePlaceholder')}
                  />
                </Field>

                <Field
                  label="Speaker preset"
                  hint="Real Qwen3 speaker original (Aiden, Ryan, Vivian…). Overrides the default speaker for the chosen voice."
                >
                  <Select
                    value={studio.qwenSpeaker ?? NONE_VALUE}
                    onValueChange={(v) => studio.setQwenSpeaker(v === NONE_VALUE ? undefined : v)}
                  >
                    <SelectTrigger><SelectValue placeholder="Auto" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value={NONE_VALUE}>Auto</SelectItem>
                      {(capabilities.data?.qwen_speakers ?? []).map((s) => (
                        <SelectItem key={s} value={s}>{formatSpeakerLabel(s)}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </Field>

                <Field
                  label="Emotion"
                  hint="Emotional tone hint blended into the Qwen3 instruction (neutral, happy, sad, calm, excited…)."
                >
                  <Select
                    value={studio.emotion ?? NONE_VALUE}
                    onValueChange={(v) => studio.setEmotion(v === NONE_VALUE ? undefined : v)}
                  >
                    <SelectTrigger><SelectValue placeholder="Neutral" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value={NONE_VALUE}>Neutral</SelectItem>
                      {(capabilities.data?.emotions ?? []).map((e) => (
                        <SelectItem key={e} value={e}>{e}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </Field>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function SegmentEditor({
  segments,
  voices,
  supportsPause,
  supportsStylePrompt,
  onAdd,
  onRemove,
  onUpdate,
}: {
  segments: SynthSegment[];
  voices: Voice[];
  supportsPause: boolean;
  supportsStylePrompt: boolean;
  onAdd: (afterId?: string) => void;
  onRemove: (id: string) => void;
  onUpdate: (id: string, patch: Partial<Omit<SynthSegment, 'id'>>) => void;
}) {
  const { t } = useTranslation();

  return (
    <div className="space-y-3">
      {segments.map((segment, index) => (
        <div key={segment.id} className="rounded-lg border bg-muted/20 p-3">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <Badge variant="secondary">{t('studio.segmentLabel', { index: index + 1 })}</Badge>
            <div className="flex items-center gap-1">
              <Button type="button" size="icon" variant="ghost" className="h-8 w-8" onClick={() => onAdd(segment.id)} title={t('studio.addSegment')}>
                <Plus className="h-4 w-4" />
              </Button>
              <Button type="button" size="icon" variant="ghost" className="h-8 w-8" onClick={() => onRemove(segment.id)} title={t('studio.removeSegment')}>
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_280px]">
            <Textarea
              value={segment.text}
              onChange={(event) => onUpdate(segment.id, { text: event.target.value })}
              placeholder={t('studio.segmentPlaceholder')}
              className="min-h-40 font-mono text-sm"
              aria-label={t('studio.segmentAria', { index: index + 1 })}
            />
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <Field label={t('studio.voice')}>
                  <SegmentVoiceSelect
                    value={segment.voice_id}
                    voices={voices}
                    onChange={(voiceId) => onUpdate(segment.id, { voice_id: voiceId })}
                  />
                </Field>
                <Field label={t('studio.tier')}>
                  <TierSelect value={segment.tier} onChange={(tier) => onUpdate(segment.id, { tier })} />
                </Field>
              </div>
              <SliderField
                label={t('studio.speed')}
                value={segment.speed}
                min={0.5} max={2} step={0.05}
                format={(value) => `${value.toFixed(2)}x`}
                onChange={(value) => onUpdate(segment.id, { speed: value })}
              />
              <SliderField
                label={t('studio.pitch')}
                value={segment.pitch}
                min={-12} max={12} step={1}
                format={(value) => `${value > 0 ? '+' : ''}${value} st`}
                onChange={(value) => onUpdate(segment.id, { pitch: value })}
              />
              <SliderField
                label={t('studio.volume')}
                value={segment.volume}
                min={0} max={2} step={0.05}
                format={(value) => `${Math.round(value * 100)}%`}
                onChange={(value) => onUpdate(segment.id, { volume: value })}
              />
              <div className="grid grid-cols-[110px_minmax(0,1fr)] gap-2">
                <Field label={t('studio.pause')}>
                  <Input
                    type="number"
                    min={0}
                    max={5000}
                    step={50}
                    value={segment.pause_after_ms}
                    disabled={!supportsPause}
                    onChange={(event) => onUpdate(segment.id, { pause_after_ms: clampPause(event.target.value) })}
                  />
                </Field>
                <Field label={t('studio.stylePrompt')}>
                  <Input
                    value={segment.style_prompt ?? ''}
                    disabled={!supportsStylePrompt}
                    onChange={(event) => onUpdate(segment.id, { style_prompt: event.target.value })}
                    placeholder={t('studio.stylePlaceholder')}
                  />
                </Field>
              </div>
            </div>
          </div>
        </div>
      ))}
      <Button type="button" variant="outline" size="sm" onClick={() => onAdd()}>
        <Plus className="h-4 w-4" /> {t('studio.addSegment')}
      </Button>
    </div>
  );
}

function SegmentVoiceSelect({ value, voices, onChange }: { value?: string; voices: Voice[]; onChange: (id?: string) => void }) {
  const { t } = useTranslation();
  return (
    <Select value={value ?? INHERIT_VOICE_VALUE} onValueChange={(next) => onChange(next === INHERIT_VOICE_VALUE ? undefined : next)}>
      <SelectTrigger><SelectValue /></SelectTrigger>
      <SelectContent>
        <SelectItem value={INHERIT_VOICE_VALUE}>{t('studio.inheritVoice')}</SelectItem>
        {voices.map((voice) => (
          <SelectItem key={voice.id} value={voice.id}>{voice.name}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

function TierSelect({ value, onChange }: { value: SynthSegment['tier']; onChange: (tier: SynthSegment['tier']) => void }) {
  const { t } = useTranslation();
  return (
    <Select value={value} onValueChange={(next) => onChange(next as SynthSegment['tier'])}>
      <SelectTrigger><SelectValue /></SelectTrigger>
      <SelectContent>
        <SelectItem value="draft">{t('studio.tiers.draft')}</SelectItem>
        <SelectItem value="standard">{t('studio.tiers.standard')}</SelectItem>
        <SelectItem value="studio">{t('studio.tiers.studio')}</SelectItem>
      </SelectContent>
    </Select>
  );
}

function clampPause(value: string): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 0;
  return Math.min(5000, Math.max(0, Math.round(parsed)));
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <Label className="flex items-center gap-1.5 text-xs font-medium uppercase tracking-wider text-muted-foreground">
        {label}
        {hint ? <HelpHint text={hint} /> : null}
      </Label>
      {children}
    </div>
  );
}

function SliderField({
  label, hint, value, onChange, min, max, step, format,
}: {
  label: string; hint?: string; value: number; onChange: (v: number) => void;
  min: number; max: number; step: number; format: (v: number) => string;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs">
        <Label className="flex items-center gap-1.5 font-medium uppercase tracking-wider text-muted-foreground">
          {label}
          {hint ? <HelpHint text={hint} /> : null}
        </Label>
        <span className="font-mono tabular-nums text-muted-foreground">{format(value)}</span>
      </div>
      <Slider value={[value]} onValueChange={(v) => onChange(v[0] ?? value)} min={min} max={max} step={step} />
    </div>
  );
}
