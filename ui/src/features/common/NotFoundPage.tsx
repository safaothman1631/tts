import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Compass } from 'lucide-react';

export function NotFoundPage() {
  return (
    <div className="container mx-auto flex h-full max-w-md flex-col items-center justify-center gap-4 p-12 text-center">
      <Compass className="h-16 w-16 text-muted-foreground" />
      <h1 className="text-3xl font-bold">404 — page not found</h1>
      <p className="text-sm text-muted-foreground">
        The page you’re looking for doesn’t exist.
      </p>
      <Button asChild variant="gradient">
        <Link to="/">Back to Studio</Link>
      </Button>
    </div>
  );
}
