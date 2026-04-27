import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Separator } from '@/components/ui/separator';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { useSettingsStore } from '@/stores/settings';
import { config } from '@/lib/config';
import { get as idbGet, set as idbSet, del as idbDel } from 'idb-keyval';
import { toast } from 'sonner';

export function SettingsPage() {
  const { t } = useTranslation();
  const s = useSettingsStore();
  const [token, setToken] = useState('');
  const [hasToken, setHasToken] = useState(false);

  useEffect(() => {
    void (async () => {
      const v = await idbGet<string>(config.storage.apiToken);
      setHasToken(!!v);
    })();
  }, []);

  const saveToken = async () => {
    if (token) {
      await idbSet(config.storage.apiToken, token);
      setHasToken(true);
      setToken('');
      toast.success('API token saved');
    }
  };
  const clearToken = async () => {
    await idbDel(config.storage.apiToken);
    setHasToken(false);
    toast.success('API token removed');
  };

  return (
    <div className="container mx-auto max-w-3xl space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold tracking-tight">{t('settings.title')}</h1>
      </header>

      <Tabs defaultValue="general">
        <TabsList>
          <TabsTrigger value="general">{t('settings.general')}</TabsTrigger>
          <TabsTrigger value="audio">{t('settings.audio')}</TabsTrigger>
          <TabsTrigger value="api">{t('settings.api')}</TabsTrigger>
          <TabsTrigger value="shortcuts">{t('settings.shortcuts')}</TabsTrigger>
          <TabsTrigger value="advanced">{t('settings.advanced')}</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader><CardTitle>{t('settings.theme')}</CardTitle></CardHeader>
            <CardContent>
              <Select value={s.theme} onValueChange={(v) => s.setTheme(v as 'light' | 'dark' | 'system')}>
                <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">{t('settings.themes.light')}</SelectItem>
                  <SelectItem value="dark">{t('settings.themes.dark')}</SelectItem>
                  <SelectItem value="system">{t('settings.themes.system')}</SelectItem>
                </SelectContent>
              </Select>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>{t('settings.language')}</CardTitle></CardHeader>
            <CardContent>
              <Select value={s.locale} onValueChange={(v) => s.setLocale(v as 'en' | 'ckb' | 'ar' | 'tr')}>
                <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="ckb">کوردی</SelectItem>
                  <SelectItem value="ar">العربية</SelectItem>
                  <SelectItem value="tr">Türkçe</SelectItem>
                </SelectContent>
              </Select>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <Label>Reduce motion</Label>
                <p className="text-xs text-muted-foreground">Disable non-essential animations.</p>
              </div>
              <Switch checked={s.reduceMotion} onCheckedChange={s.setReduceMotion} />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <Label>High contrast</Label>
                <p className="text-xs text-muted-foreground">Maximum readability for accessibility.</p>
              </div>
              <Switch checked={s.highContrast} onCheckedChange={s.setHighContrast} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audio" className="space-y-4">
          <Card>
            <CardHeader><CardTitle>Defaults</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Format</Label>
                <Select value={s.defaultFormat} onValueChange={(v) => s.setDefaultFormat(v as 'wav' | 'mp3' | 'flac' | 'ogg')}>
                  <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="wav">WAV</SelectItem>
                    <SelectItem value="mp3">MP3</SelectItem>
                    <SelectItem value="flac">FLAC</SelectItem>
                    <SelectItem value="ogg">OGG</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Tier</Label>
                <Select value={s.defaultTier} onValueChange={(v) => s.setDefaultTier(v as 'draft' | 'standard' | 'studio')}>
                  <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="standard">Standard</SelectItem>
                    <SelectItem value="studio">Studio</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Separator />
              <RangeRow label="Speed" value={s.defaultSpeed} min={0.5} max={2} step={0.05} onChange={(v) => s.setDefaults({ defaultSpeed: v })} format={(v) => `${v.toFixed(2)}×`} />
              <RangeRow label="Pitch" value={s.defaultPitch} min={-12} max={12} step={1} onChange={(v) => s.setDefaults({ defaultPitch: v })} format={(v) => `${v} st`} />
              <RangeRow label="Volume" value={s.defaultVolume} min={0} max={2} step={0.05} onChange={(v) => s.setDefaults({ defaultVolume: v })} format={(v) => `${Math.round(v * 100)}%`} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader><CardTitle>API token</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Token is stored locally (IndexedDB) and sent as <code>Authorization: Bearer …</code>.
              </p>
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                <Input type="password" value={token} onChange={(e) => setToken(e.target.value)} placeholder={hasToken ? 'A token is already saved' : 'Enter token'} />
                <Button onClick={saveToken} disabled={!token}>Save</Button>
                {hasToken && <Button variant="outline" onClick={clearToken}>Clear</Button>}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Endpoint</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm text-muted-foreground">Base URL:</p>
              <code className="block rounded-md bg-muted px-3 py-2 text-xs">{config.apiBaseUrl}</code>
              <p className="text-sm text-muted-foreground mt-2">WebSocket:</p>
              <code className="block rounded-md bg-muted px-3 py-2 text-xs">{config.wsBaseUrl}</code>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="shortcuts">
          <Card>
            <CardContent className="p-0">
              <table className="w-full text-sm">
                <thead className="border-b text-xs text-muted-foreground">
                  <tr><th className="p-3 text-start">Action</th><th className="p-3 text-start">Shortcut</th></tr>
                </thead>
                <tbody>
                  {Object.entries(config.shortcuts).map(([k, v]) => (
                    <tr key={k} className="border-b">
                      <td className="p-3 capitalize">{k}</td>
                      <td className="p-3"><code className="rounded bg-muted px-2 py-0.5 text-xs">{v}</code></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced">
          <Card>
            <CardHeader><CardTitle>Reset</CardTitle></CardHeader>
            <CardContent>
              <Button variant="destructive" onClick={() => { s.reset(); toast.success('Settings reset'); }}>
                Reset all settings
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function RangeRow({
  label, value, onChange, min, max, step, format,
}: {
  label: string; value: number; onChange: (v: number) => void;
  min: number; max: number; step: number; format: (v: number) => string;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label>{label}</Label>
        <span className="font-mono text-xs tabular-nums text-muted-foreground">{format(value)}</span>
      </div>
      <Slider value={[value]} onValueChange={(v) => onChange(v[0] ?? value)} min={min} max={max} step={step} />
    </div>
  );
}
