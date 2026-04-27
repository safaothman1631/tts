import { useMutation } from '@tanstack/react-query';
import { synthesize, synthesizeSegments, streamSynthesize } from '@/api/endpoints';
import { useStudioStore } from '@/stores/studio';
import { useHistoryStore } from '@/stores/history';
import { audioExtensionFromBlob, uid } from '@/lib/utils';
import { toast } from 'sonner';

interface SynthOptions {
  /** Use HTTP chunked streaming (`/v1/stream`). Defaults to false. */
  stream?: boolean;
  /** Save the previous audio as the A/B "B" slot before replacing. */
  keepPrevious?: boolean;
}

export function useSynthesize() {
  const buildRequest = useStudioStore((s) => s.buildRequest);
  const buildSegmentsRequest = useStudioStore((s) => s.buildSegmentsRequest);
  const segmentsMode = useStudioStore((s) => s.segmentsMode);
  const setSynthesizing = useStudioStore((s) => s.setSynthesizing);
  const setAudio = useStudioStore((s) => s.setAudio);
  const setStreamProgress = useStudioStore((s) => s.setStreamProgress);
  const setCompare = useStudioStore((s) => s.setCompare);
  const addHistory = useHistoryStore((s) => s.add);

  return useMutation({
    mutationFn: async (opts: SynthOptions = {}) => {
      const req = buildRequest();
      const segmentReq = segmentsMode ? buildSegmentsRequest() : undefined;
      const inputText = segmentsMode ? segmentReq?.segments.map((segment) => segment.text).join('\n\n') : req.text;
      if (!inputText?.trim()) throw { status: 0, message: 'Text is empty' };
      setSynthesizing(true);

      // Snapshot the previous take for A/B compare if requested.
      if (opts.keepPrevious) {
        const { currentAudioUrl, currentAudioBlob } = useStudioStore.getState();
        if (currentAudioBlob || currentAudioUrl) setCompare(currentAudioUrl, 'Previous take', currentAudioBlob);
      }

      let blob: Blob;
      let durationSeconds: number | undefined;

      if (segmentsMode) {
        const result = await synthesizeSegments(segmentReq!);
        blob = result.blob;
        durationSeconds = result.meta.duration_seconds;
      } else if (opts.stream) {
        setStreamProgress(0);
        const start = performance.now();
        const result = await streamSynthesize(req, (_chunk, total) => {
          // We do not know the final size; show indeterminate "growing" progress.
          const grown = Math.min(0.95, total / 200_000);
          setStreamProgress(grown);
        });
        blob = result.blob;
        durationSeconds = (performance.now() - start) / 1000;
        setStreamProgress(1);
      } else {
        const r = await synthesize(req);
        blob = r.blob;
        durationSeconds = r.meta.duration_seconds;
      }

      setAudio(undefined, durationSeconds, blob);
      await addHistory({
        id: uid(),
        text: inputText,
        voiceId: segmentsMode ? segmentReq?.segments[0]?.voice_id : req.voice_id,
        format: audioExtensionFromBlob(blob, segmentsMode ? 'wav' : req.format),
        durationSeconds,
        createdAt: Date.now(),
        audioBlob: blob,
      });
      return { url: undefined, durationSeconds };
    },
    onError: (err: { message?: string }) => {
      toast.error(err?.message ?? 'Synthesis failed');
    },
    onSettled: () => {
      setSynthesizing(false);
      setStreamProgress(undefined);
    },
  });
}
