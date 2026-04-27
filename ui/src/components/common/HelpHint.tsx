import { HelpCircle } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

export interface HelpHintProps {
  /** The hint text shown on hover/focus. */
  text: string;
  /** Optional accessible label override. */
  label?: string;
  /** Additional class names for the trigger button. */
  className?: string;
  /** Tooltip side. */
  side?: 'top' | 'right' | 'bottom' | 'left';
}

/**
 * Tiny circular help icon that surfaces a tooltip explaining a setting or
 * button. Designed to live next to labels throughout the studio so every
 * control documents itself in-place.
 */
export function HelpHint({ text, label, className, side = 'top' }: HelpHintProps) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button
          type="button"
          aria-label={label ?? text}
          className={cn(
            'inline-flex h-4 w-4 items-center justify-center rounded-full text-muted-foreground/70 transition-colors hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-primary',
            className,
          )}
          tabIndex={0}
        >
          <HelpCircle className="h-3.5 w-3.5" />
        </button>
      </TooltipTrigger>
      <TooltipContent side={side} className="max-w-xs text-xs leading-relaxed">
        {text}
      </TooltipContent>
    </Tooltip>
  );
}
