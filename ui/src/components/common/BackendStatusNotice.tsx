import { AlertTriangle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn } from '@/lib/utils';

interface BackendStatusNoticeProps {
  message: string;
  className?: string;
}

export function BackendStatusNotice({ message, className }: BackendStatusNoticeProps) {
  const { t } = useTranslation();
  return (
    <div className={cn('rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-xs text-destructive', className)}>
      <div className="flex items-center gap-1.5 font-medium">
        <AlertTriangle className="h-3.5 w-3.5" />
        {t('common.backendUnavailable')}
      </div>
      <p className="mt-1 text-[11px] opacity-90">{message}</p>
    </div>
  );
}
