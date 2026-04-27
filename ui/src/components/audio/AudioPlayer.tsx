import { useEffect, useRef, useState } from 'react';
import { Play, Pause, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { useStudioStore } from '@/stores/studio';
import { formatDuration } from '@/lib/utils';

interface AudioPlayerProps {
  url?: string;
  blob?: Blob;
  format?: string;
}

export function AudioPlayer({ url, blob }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const loadSeqRef = useRef(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [current, setCurrent] = useState(0);
  const [volume, setVolume] = useState(1);
  const [loadError, setLoadError] = useState<string | null>(null);
  const setStorePlaying = useStudioStore((s) => s.setPlaying);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const onLoaded = () => {
      setDuration(Number.isFinite(audio.duration) ? audio.duration : 0);
      setCurrent(0);
      setLoadError(null);
    };
    const onTime = () => setCurrent(audio.currentTime || 0);
    const onPlay = () => {
      setIsPlaying(true);
      setStorePlaying(true);
    };
    const onPause = () => {
      setIsPlaying(false);
      setStorePlaying(false);
    };
    const onEnded = () => {
      setIsPlaying(false);
      setStorePlaying(false);
    };
    const onError = () => setLoadError('Audio could not be loaded');

    audio.addEventListener('loadedmetadata', onLoaded);
    audio.addEventListener('timeupdate', onTime);
    audio.addEventListener('play', onPlay);
    audio.addEventListener('pause', onPause);
    audio.addEventListener('ended', onEnded);
    audio.addEventListener('error', onError);

    return () => {
      audio.removeEventListener('loadedmetadata', onLoaded);
      audio.removeEventListener('timeupdate', onTime);
      audio.removeEventListener('play', onPlay);
      audio.removeEventListener('pause', onPause);
      audio.removeEventListener('ended', onEnded);
      audio.removeEventListener('error', onError);
      setStorePlaying(false);
    };
  }, [setStorePlaying]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const seq = ++loadSeqRef.current;

    setIsPlaying(false);
    setCurrent(0);
    setDuration(0);
    setLoadError(null);

    if (blob) {
      const safeBlob = blob.type ? blob : new Blob([blob], { type: 'audio/wav' });
      void blobToDataUrl(safeBlob)
        .then((dataUrl) => {
          if (!audioRef.current || seq !== loadSeqRef.current) return;
          audioRef.current.src = dataUrl;
          audioRef.current.load();
        })
        .catch(() => {
          if (!audioRef.current || seq !== loadSeqRef.current) return;
          setLoadError('Audio could not be loaded');
        });
      return;
    }

    audio.src = url ?? '';
    if (url) audio.load();
  }, [blob, url]);

  useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume;
  }, [volume]);

  const toggle = () => {
    const audio = audioRef.current;
    if (!audio || !hasAudio) return;
    if (audio.paused) {
      void audio.play().catch(() => setLoadError('Audio could not be played'));
      return;
    }
    audio.pause();
  };

  const restart = () => {
    const audio = audioRef.current;
    if (!audio || !hasAudio) return;
    audio.currentTime = 0;
    if (!isPlaying) void audio.play().catch(() => setLoadError('Audio could not be played'));
  };

  const handleDownload = async () => {
    // Intentionally a no-op. Downloads are exposed through the parent's
    // dedicated Download button to keep the player play-only.
  };
  void handleDownload;

  const hasAudio = Boolean(blob || url);

  return (
    <div className="space-y-3 rounded-xl border bg-card p-4">
      <audio
        ref={audioRef}
        controls
        controlsList="nodownload noplaybackrate noremoteplayback"
        preload="metadata"
        className="w-full"
      />
      {loadError && <div className="text-xs text-destructive">{loadError}</div>}
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-1">
          <Button type="button" size="icon" variant="ghost" onClick={toggle} disabled={!hasAudio} aria-label={isPlaying ? 'Pause' : 'Play'}>
            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>
          <Button type="button" size="icon" variant="ghost" onClick={restart} disabled={!hasAudio} aria-label="Restart">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
        <div className="flex-1 text-center font-mono text-xs tabular-nums text-muted-foreground">
          {formatDuration(current)} / {formatDuration(duration)}
        </div>
        <div className="flex w-32 items-center gap-2">
          <Slider
            value={[volume * 100]}
            onValueChange={(v) => setVolume((v[0] ?? 100) / 100)}
            min={0}
            max={100}
            step={1}
            aria-label="Volume"
          />
        </div>
      </div>
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
