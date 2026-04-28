import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Mic, Square, Check, ChevronRight, ChevronLeft, AlertTriangle, Loader2, Play, Pause, Upload } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { HelpHint } from '@/components/common/HelpHint';
import { SampleTextPicker } from '@/components/common/SampleTextPicker';
import { cn, formatDuration } from '@/lib/utils';
import { toast } from 'sonner';
import { cloneVoice, deleteVoice, synthesize } from '@/api/endpoints';
import { useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/hooks/queries';
import { useStudioStore } from '@/stores/studio';
import { useNavigate } from 'react-router-dom';
import type { Voice } from '@/types/api';

const STEPS = ['intro', 'record', 'review', 'name', 'test'] as const;
type Step = typeof STEPS[number];

const LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'ckb', label: 'کوردی' },
  { value: 'ar', label: 'العربية' },
  { value: 'tr', label: 'Türkçe' },
  { value: 'zh', label: '中文' },
  { value: 'ja', label: '日本語' },
  { value: 'de', label: 'Deutsch' },
  { value: 'fr', label: 'Français' },
  { value: 'es', label: 'Español' },
];

const DEFAULT_TEST_TEXT = 'Hello, this is a test of my new custom voice.';

export function VoiceLabPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const setStudioVoice = useStudioStore((s) => s.setVoice);
  const [step, setStep] = useState<Step>('intro');
  const [consent, setConsent] = useState(false);
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('en');
  const [referenceText, setReferenceText] = useState('');
  const [recorder, setRecorder] = useState<MediaRecorder | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [createdVoice, setCreatedVoice] = useState<Voice | null>(null);
  const [testText, setTestText] = useState(DEFAULT_TEST_TEXT);
  const [testSynthesizing, setTestSynthesizing] = useState(false);
  const [testAudioUrl, setTestAudioUrl] = useState<string | null>(null);
  const [testPlaying, setTestPlaying] = useState(false);
  const queryClient = useQueryClient();
  const audioUrlRef = useRef<string | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const testAudioElRef = useRef<HTMLAudioElement | null>(null);
  const testAudioUrlRef = useRef<string | null>(null);

  const idx = STEPS.indexOf(step);

  useEffect(() => {
    audioUrlRef.current = audioUrl;
  }, [audioUrl]);

  useEffect(() => {
    recorderRef.current = recorder;
  }, [recorder]);

  useEffect(() => {
    streamRef.current = stream;
  }, [stream]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current);
      if (testAudioUrlRef.current) URL.revokeObjectURL(testAudioUrlRef.current);
      if (streamRef.current) streamRef.current.getTracks().forEach((tr) => tr.stop());
      if (recorderRef.current && recorderRef.current.state !== 'inactive') recorderRef.current.stop();
    };
  }, []);

  useEffect(() => {
    testAudioUrlRef.current = testAudioUrl;
  }, [testAudioUrl]);

  const resetWizard = () => {
    setStep('intro');
    setConsent(false);
    setAudioBlob(null);
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(null);
    setDuration(0);
    setName('');
    setDescription('');
    setReferenceText('');
    setLanguage('en');
    setCreatedVoice(null);
    setTestText(DEFAULT_TEST_TEXT);
    if (testAudioUrl) URL.revokeObjectURL(testAudioUrl);
    setTestAudioUrl(null);
    setTestPlaying(false);
  };

  const runTestSynthesis = async () => {
    if (!createdVoice) {
      toast.error('Create the voice first.');
      return;
    }
    if (!testText.trim()) {
      toast.error('Enter some text to test.');
      return;
    }
    setTestSynthesizing(true);
    try {
      const { blob } = await synthesize({
        text: testText,
        voice_id: createdVoice.id,
        format: 'wav',
        tier: 'studio',
        speed: 1,
        pitch: 0,
        volume: 1,
        ssml: false,
        language,
      });
      if (testAudioUrl) URL.revokeObjectURL(testAudioUrl);
      const url = URL.createObjectURL(blob);
      setTestAudioUrl(url);
      setTimeout(() => {
        const el = testAudioElRef.current;
        if (el) {
          el.src = url;
          el.load();
          void el.play().catch(() => undefined);
        }
      }, 50);
    } catch (e) {
      const msg = (e as { message?: string })?.message ?? 'Test synthesis failed';
      toast.error(msg);
    } finally {
      setTestSynthesizing(false);
    }
  };

  const removeCreatedVoice = async () => {
    if (!createdVoice) return;
    try {
      if (!createdVoice.id.startsWith('local-')) {
        await deleteVoice(createdVoice.id);
      }
      queryClient.invalidateQueries({ queryKey: queryKeys.voices });
      toast.success('Voice deleted.');
      resetWizard();
    } catch (e) {
      const msg = (e as { message?: string })?.message ?? 'Could not delete voice';
      toast.error(msg);
    }
  };

  const start = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(mediaStream);
      const chunks: Blob[] = [];
      const startedAt = Date.now();
      mr.addEventListener('dataavailable', (e) => chunks.push(e.data));
      mr.addEventListener('stop', () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        setAudioBlob(blob);
        if (audioUrl) URL.revokeObjectURL(audioUrl);
        setAudioUrl(URL.createObjectURL(blob));
        setDuration((Date.now() - startedAt) / 1000);
      });
      mr.start();
      setStream(mediaStream);
      setRecorder(mr);
      setRecording(true);
    } catch {
      toast.error('Microphone unavailable');
    }
  };

  const stop = () => {
    recorder?.stop();
    setRecording(false);
  };

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const onPickFile = () => {
    fileInputRef.current?.click();
  };

  const onFileChosen = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    // Always reset the input so picking the same file twice still fires onChange.
    event.target.value = '';
    if (!file) return;

    // Hard validation: type + size (cap at 50 MB to avoid UI lockups).
    if (!file.type.startsWith('audio/') && !/\.(wav|mp3|m4a|ogg|flac|webm)$/i.test(file.name)) {
      toast.error('Please choose an audio file (wav, mp3, m4a, ogg, flac, webm).');
      return;
    }
    const MAX_BYTES = 50 * 1024 * 1024;
    if (file.size > MAX_BYTES) {
      toast.error('File is larger than 50 MB. Please trim it first.');
      return;
    }

    // Stop any active recording before swapping in the upload.
    if (recording) stop();

    if (audioUrl) URL.revokeObjectURL(audioUrl);
    const url = URL.createObjectURL(file);
    setAudioBlob(file);
    setAudioUrl(url);

    // Best-effort duration probe via a transient <audio> element.
    try {
      const probe = document.createElement('audio');
      probe.preload = 'metadata';
      probe.src = url;
      const dur = await new Promise<number>((resolve, reject) => {
        const cleanup = () => {
          probe.removeEventListener('loadedmetadata', onMeta);
          probe.removeEventListener('error', onErr);
        };
        const onMeta = () => {
          cleanup();
          resolve(Number.isFinite(probe.duration) ? probe.duration : 0);
        };
        const onErr = () => {
          cleanup();
          reject(new Error('decode-failed'));
        };
        probe.addEventListener('loadedmetadata', onMeta);
        probe.addEventListener('error', onErr);
      });
      setDuration(dur);
      if (dur > 0 && dur < 5) {
        toast.warning(`Sample is only ${dur.toFixed(1)}s. 30+ seconds gives much better cloning quality.`);
      }
    } catch {
      // Some containers (e.g. raw webm) don't expose duration; leave 0 and let user proceed.
      setDuration(0);
    }
    toast.success(`Loaded ${file.name}`);
  };

  const next = () => {
    if (step === 'intro' && !consent) {
      toast.error('Please accept the consent.');
      return;
    }
    if (step === 'record' && !audioBlob) {
      toast.error('Record a sample first.');
      return;
    }
    if (step === 'name' && !name.trim()) {
      toast.error('Give your voice a name.');
      return;
    }
    setStep(STEPS[Math.min(idx + 1, STEPS.length - 1)] as Step);
  };

  const back = () => {
    // Stop recording if going back from record step
    if (step === 'record' && recording) {
      stop();
    }
    setStep(STEPS[Math.max(idx - 1, 0)] as Step);
  };

  return (
    <div className="container mx-auto max-w-3xl space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold tracking-tight">{t('voiceLab.title')}</h1>
        <p className="text-sm text-muted-foreground">{t('voiceLab.intro')}</p>
      </header>

      <div className="flex items-center justify-between">
        {STEPS.map((s, i) => (
          <div key={s} className="flex flex-1 items-center">
            <div
              className={cn(
                'flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold transition-colors',
                i <= idx ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground',
              )}
            >
              {i < idx ? <Check className="h-4 w-4" /> : i + 1}
            </div>
            {i < STEPS.length - 1 && (
              <div className={cn('mx-2 h-0.5 flex-1', i < idx ? 'bg-primary' : 'bg-muted')} />
            )}
          </div>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            {step === 'intro' && t('voiceLab.step1')}
            {step === 'record' && t('voiceLab.step2')}
            {step === 'review' && t('voiceLab.step3')}
            {step === 'name' && t('voiceLab.step4')}
            {step === 'test' && t('voiceLab.step5')}
          </CardTitle>
          <CardDescription>Step {idx + 1} of {STEPS.length}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {step === 'intro' && (
            <>
              <div className="rounded-lg border border-warning/30 bg-warning/5 p-4 text-sm">
                <div className="flex items-center gap-2 font-medium text-warning">
                  <AlertTriangle className="h-4 w-4" /> Ethics & consent
                </div>
                <p className="mt-2 text-muted-foreground">
                  Voice cloning may only be used with explicit consent of the speaker. Misuse for
                  impersonation, fraud, or harassment is strictly forbidden.
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Switch id="consent" checked={consent} onCheckedChange={setConsent} />
                <Label htmlFor="consent" className="text-sm">{t('voiceLab.consent')}</Label>
              </div>
            </>
          )}

          {step === 'record' && (
            <div className="flex flex-col items-center gap-4 py-6">
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*,.wav,.mp3,.m4a,.ogg,.flac,.webm"
                className="hidden"
                onChange={onFileChosen}
                aria-label="Upload audio sample"
              />
              <Button
                size="xl"
                variant={recording ? 'destructive' : 'gradient'}
                onClick={recording ? stop : start}
                className="h-24 w-24 rounded-full"
              >
                {recording ? <Square className="h-8 w-8" /> : <Mic className="h-8 w-8" />}
              </Button>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span className="h-px w-8 bg-border" /> or <span className="h-px w-8 bg-border" />
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={onPickFile}
                disabled={recording}
              >
                <Upload className="h-4 w-4" /> Upload audio file
              </Button>
              <div className="text-sm text-muted-foreground">
                {recording
                  ? 'Recording…'
                  : audioBlob
                    ? `Loaded ${duration > 0 ? formatDuration(duration) : '(unknown duration)'}`
                    : 'Record at least 30 seconds, or upload a clean audio file (WAV/MP3/M4A/OGG/FLAC).'}
              </div>
              {audioUrl && !recording && (
                <audio controls controlsList="nodownload noremoteplayback" src={audioUrl} className="w-full" />
              )}
            </div>
          )}

          {step === 'review' && (
            <div className="space-y-3">
              <div className="text-sm">Listen back and confirm quality is acceptable.</div>
              {audioUrl && (
                <audio controls controlsList="nodownload noremoteplayback" src={audioUrl} className="w-full" />
              )}
              <Button variant="outline" size="sm" onClick={() => setStep('record')}>Re-record</Button>
            </div>
          )}

          {step === 'name' && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="vname" className="flex items-center gap-1.5">
                  Voice name
                  <HelpHint text="Display name shown across the voice library and Studio. Letters, digits and spaces only." />
                </Label>
                <Input id="vname" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Aria" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="vdesc" className="flex items-center gap-1.5">
                  Description (optional)
                  <HelpHint text="Short description shown on the voice card. Useful when you have multiple custom voices." />
                </Label>
                <Input id="vdesc" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Warm storytelling voice for audiobooks…" />
              </div>
              <div className="space-y-2">
                <Label className="flex items-center gap-1.5">
                  Primary language
                  <HelpHint text="Language the recording is in. Helps Qwen3 pick the right phonemizer when cloning." />
                </Label>
                <Select value={language} onValueChange={setLanguage}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {LANGUAGE_OPTIONS.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="vref" className="flex items-center gap-1.5">
                  Reference transcript (optional)
                  <HelpHint text="Exact text spoken in the reference recording. Improves clone quality on Qwen3 by aligning audio with text." />
                </Label>
                <SampleTextPicker onPick={(s) => setReferenceText(s.text)} compact />
                <Textarea
                  id="vref"
                  value={referenceText}
                  onChange={(e) => setReferenceText(e.target.value)}
                  placeholder="Type what you said in the recording…"
                  className="min-h-20 text-sm"
                />
              </div>
            </div>
          )}

          {step === 'test' && (
            <div className="space-y-4">
              {!createdVoice ? (
                <div className="space-y-3 text-sm">
                  <p>Voice <strong>{name || 'Unnamed'}</strong> is ready to be created.</p>
                  <p className="text-muted-foreground">
                    Your recording will be saved to the local voice list. If the backend clone endpoint
                    becomes available, it will be uploaded automatically.
                  </p>
                </div>
              ) : (
                <>
                  <div className="rounded-lg border border-success/30 bg-success/5 p-3 text-sm">
                    <div className="font-medium text-success">✓ Voice created: {createdVoice.name}</div>
                    <div className="text-xs text-muted-foreground">
                      Backend: {createdVoice.backend} · Language: {createdVoice.language}
                      {createdVoice.id.startsWith('local-') ? ' · Saved locally' : ' · Persisted on server'}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="vtest" className="flex items-center gap-1.5">
                      Test phrase
                      <HelpHint text="Synthesize a sentence with the new voice to verify quality before using it in Studio." />
                    </Label>
                    <SampleTextPicker
                      onPick={(s) => setTestText(s.text)}
                      disabled={testSynthesizing}
                      compact
                    />
                    <Textarea
                      id="vtest"
                      value={testText}
                      onChange={(e) => setTestText(e.target.value)}
                      className="min-h-20 text-sm"
                    />
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <Button onClick={() => void runTestSynthesis()} disabled={testSynthesizing}>
                      {testSynthesizing ? <><Loader2 className="h-4 w-4 animate-spin" /> Synthesizing…</> : <><Play className="h-4 w-4" /> Test voice</>}
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => {
                        setStudioVoice(createdVoice.id);
                        navigate('/');
                      }}
                    >
                      Use in Studio
                    </Button>
                    <Button variant="ghost" onClick={resetWizard}>
                      Start over
                    </Button>
                    <Button variant="destructive" onClick={() => void removeCreatedVoice()}>
                      Delete voice
                    </Button>
                  </div>
                  {testAudioUrl && (
                    <audio
                      ref={testAudioElRef}
                      controls
                      controlsList="nodownload noremoteplayback"
                      className="w-full"
                      onPlay={() => setTestPlaying(true)}
                      onPause={() => setTestPlaying(false)}
                      onEnded={() => setTestPlaying(false)}
                    />
                  )}
                  {testPlaying && (
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Pause className="h-3 w-3" /> Playing test sample…
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="flex justify-between">
        <Button variant="outline" disabled={idx === 0} onClick={back}>
          <ChevronLeft className="h-4 w-4" /> {t('actions.back')}
        </Button>
        {step === 'test' ? (
          createdVoice ? null : (
            <Button
              variant="gradient"
              disabled={submitting || !audioBlob}
              onClick={async () => {
                if (!audioBlob) return;
                setSubmitting(true);
                try {
                  const result = await cloneVoice({
                    name: name.trim() || 'Untitled',
                    description: description.trim() || undefined,
                    audioBlob,
                    consent,
                    language,
                    referenceText: referenceText.trim() || undefined,
                  });
                  setCreatedVoice(result.voice);
                  queryClient.invalidateQueries({ queryKey: queryKeys.voices });
                  const msg = result.isLocal
                    ? `Voice "${result.voice.name}" saved locally (clone endpoint unavailable).`
                    : `Voice "${result.voice.name}" created on backend.`;
                  toast.success(msg);
                } catch (e) {
                  const errMsg = (e as { message?: string })?.message ?? 'Voice creation failed';
                  toast.error(errMsg);
                } finally {
                  setSubmitting(false);
                }
              }}
            >
              {submitting ? <><Loader2 className="h-4 w-4 animate-spin" /> Uploading…</> : t('actions.finish')}
            </Button>
          )
        ) : (
          <Button onClick={next}>
            {t('actions.next')} <ChevronRight className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
