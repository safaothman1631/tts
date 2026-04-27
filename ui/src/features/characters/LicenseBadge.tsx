import { Badge } from '@/components/ui/badge';

const LICENSE_STYLE: Record<string, { label: string; className: string; tooltip: string }> = {
  PD:               { label: 'PD',       className: 'bg-emerald-600 text-white',   tooltip: 'Public domain — no restrictions.' },
  CC0:              { label: 'CC0',      className: 'bg-sky-600 text-white',       tooltip: 'CC0 — public-domain dedication, no attribution required.' },
  'CC-BY-4.0':      { label: 'CC-BY',    className: 'bg-amber-500 text-black',     tooltip: 'CC-BY 4.0 — attribution required in distributions.' },
  'CC-BY-3.0':      { label: 'CC-BY 3',  className: 'bg-amber-500 text-black',     tooltip: 'CC-BY 3.0 — attribution required.' },
  custom_owned:     { label: 'Owned',    className: 'bg-violet-600 text-white',    tooltip: 'You own / have permission to use this voice.' },
  pending_clone:    { label: 'Archetype', className: 'bg-zinc-700 text-zinc-100 border border-zinc-500', tooltip: 'Archetype slot — awaiting reference clip ingestion. Currently using a synth-only fallback voice.' },
  synthetic_only:   { label: 'Synth',    className: 'bg-zinc-600 text-zinc-100',   tooltip: 'Synthetic voice (no human reference). Safe to ship.' },
};

export interface LicenseBadgeProps {
  license: string;
  attributionRequired?: boolean;
  attributionString?: string | null;
  className?: string;
}

export function LicenseBadge({ license, attributionRequired, attributionString, className }: LicenseBadgeProps) {
  const style = LICENSE_STYLE[license] ?? LICENSE_STYLE.synthetic_only ?? { label: license, className: 'bg-zinc-600 text-zinc-100', tooltip: '' };
  const tooltip = attributionString
    ? `${style.tooltip}\nAttribution: ${attributionString}`
    : attributionRequired
    ? `${style.tooltip}\nAttribution required.`
    : style.tooltip;
  return (
    <Badge
      title={tooltip}
      className={`h-5 px-1.5 text-[10px] font-semibold ${style.className} ${className ?? ''}`}
    >
      {style.label}
    </Badge>
  );
}
