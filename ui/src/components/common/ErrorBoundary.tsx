import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertOctagon, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface State { error?: Error }

export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = {};

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
     
    console.error('UI error boundary:', error, info);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="flex h-screen w-screen items-center justify-center p-6">
        <div className="max-w-md space-y-3 rounded-xl border bg-card p-6 text-center shadow-lg">
          <AlertOctagon className="mx-auto h-10 w-10 text-destructive" />
          <h1 className="text-lg font-semibold">Something went wrong</h1>
          <p className="text-sm text-muted-foreground">{this.state.error.message}</p>
          <Button variant="gradient" onClick={() => location.reload()}>
            <RefreshCw className="h-4 w-4" /> Reload
          </Button>
        </div>
      </div>
    );
  }
}
