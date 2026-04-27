import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Trash2, Play, Download, FileDown } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useHistoryStore } from '@/stores/history';
import { audioExtensionFromBlob, downloadBlob, formatDuration, truncate } from '@/lib/utils';
import { useStudioStore } from '@/stores/studio';

export function HistoryPage() {
  const { t } = useTranslation();
  const { items, load, remove, clear } = useHistoryStore();
  const setText = useStudioStore((s) => s.setText);
  const setAudio = useStudioStore((s) => s.setAudio);

  useEffect(() => { void load(); }, [load]);

  const replay = (id: string) => {
    const item = items.find((i) => i.id === id);
    if (!item) return;
    setText(item.text);
    if (item.audioBlob) setAudio(undefined, item.durationSeconds, item.audioBlob);
  };

  const dl = (id: string) => {
    const item = items.find((i) => i.id === id);
    if (!item?.audioBlob) return;
    const ext = audioExtensionFromBlob(item.audioBlob, item.format);
    downloadBlob(item.audioBlob, `tts-${item.id}.${ext}`);
  };

  const removeItem = async (id: string) => {
    if (!window.confirm('Delete this history item?')) return;
    await remove(id);
  };

  const clearAll = async () => {
    if (!window.confirm('Clear all synthesis history?')) return;
    await clear();
  };

  const exportAll = () => {
    const data = items.map((item) => {
      const { audioBlob: _omit, ...rest } = item;
      void _omit;
      return rest;
    });
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    downloadBlob(blob, `tts-history-${Date.now()}.json`);
  };

  return (
    <div className="container mx-auto max-w-4xl space-y-4 p-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">{t('history.title')}</h1>
        {items.length > 0 && (
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={exportAll}>
              <FileDown className="h-4 w-4" /> Export
            </Button>
            <Button variant="outline" size="sm" onClick={() => void clearAll()}>
              <Trash2 className="h-4 w-4" /> {t('history.clearAll')}
            </Button>
          </div>
        )}
      </header>

      {items.length === 0 ? (
        <div className="flex h-60 items-center justify-center rounded-lg border-2 border-dashed text-sm text-muted-foreground">
          {t('history.empty')}
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <Card key={item.id} className="transition-colors hover:bg-accent/30">
              <CardContent className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="min-w-0 flex-1">
                  <div className="text-sm">{truncate(item.text, 120)}</div>
                  <div className="mt-1 flex gap-2 text-xs text-muted-foreground">
                    <span>{new Date(item.createdAt).toLocaleString()}</span>
                    <span>·</span>
                    <span>{item.format.toUpperCase()}</span>
                    {item.durationSeconds && <><span>·</span><span>{formatDuration(item.durationSeconds)}</span></>}
                  </div>
                </div>
                <div className="flex gap-1">
                  <Button size="icon" variant="ghost" onClick={() => replay(item.id)} aria-label="Replay">
                    <Play className="h-4 w-4" />
                  </Button>
                  <Button size="icon" variant="ghost" onClick={() => dl(item.id)} aria-label="Download" disabled={!item.audioBlob}>
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button size="icon" variant="ghost" onClick={() => void removeItem(item.id)} aria-label="Delete">
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
