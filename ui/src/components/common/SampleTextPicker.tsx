import { Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { SAMPLE_TEXTS, type SampleText } from '@/lib/sample-texts';

interface SampleTextPickerProps {
  /** Called when the user clicks a sample. */
  onPick: (sample: SampleText) => void;
  /** Optional label rendered before the chips. Defaults to "Samples". */
  label?: string;
  /** Restrict to a subset of samples by id. Defaults to all 5. */
  ids?: string[];
  /** Extra wrapper className. */
  className?: string;
  /** Disable all chips (e.g. while a request is in-flight). */
  disabled?: boolean;
  /** Smaller vertical padding for inline use inside dense forms. */
  compact?: boolean;
}

/**
 * Compact row of clickable sample-text chips. Each chip fills the parent
 * input/textarea via the supplied `onPick` callback.
 */
export function SampleTextPicker({
  onPick,
  label = 'Samples',
  ids,
  className,
  disabled,
  compact,
}: SampleTextPickerProps) {
  const items = ids
    ? SAMPLE_TEXTS.filter((s) => ids.includes(s.id))
    : SAMPLE_TEXTS;

  if (items.length === 0) return null;

  return (
    <div
      className={cn(
        'flex flex-wrap items-center gap-1.5',
        compact ? 'py-0.5' : 'py-1',
        className,
      )}
      role="group"
      aria-label={label}
    >
      <span className="flex items-center gap-1 text-xs font-medium text-muted-foreground">
        <Sparkles className="h-3 w-3" aria-hidden /> {label}:
      </span>
      {items.map((sample) => (
        <Button
          key={sample.id}
          type="button"
          variant="outline"
          size="sm"
          disabled={disabled}
          className="h-7 px-2 text-xs"
          onClick={() => onPick(sample)}
          title={sample.text}
        >
          {sample.label}
        </Button>
      ))}
    </div>
  );
}
