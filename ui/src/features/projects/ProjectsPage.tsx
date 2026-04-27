import { useState, useEffect } from 'react';
import { Plus, FolderOpen, Trash2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { get as idbGet, set as idbSet } from 'idb-keyval';
import { toast } from 'sonner';
import { uid } from '@/lib/utils';

interface Project {
  id: string;
  title: string;
  chapters: { id: string; title: string; text: string }[];
  createdAt: number;
}

const KEY = 'tts-studio:projects';

export function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState('');

  useEffect(() => {
    void (async () => {
      const data = (await idbGet<Project[]>(KEY)) ?? [];
      setProjects(data);
    })();
  }, []);

  const persist = async (p: Project[]) => {
    setProjects(p);
    await idbSet(KEY, p);
  };

  const create = async () => {
    if (!title.trim()) return;
    const proj: Project = {
      id: uid(),
      title: title.trim(),
      chapters: [{ id: uid(), title: 'Chapter 1', text: '' }],
      createdAt: Date.now(),
    };
    await persist([proj, ...projects]);
    setTitle('');
    setOpen(false);
    toast.success('Project created');
  };

  const remove = async (id: string) => {
    if (!window.confirm('Delete this project?')) return;
    await persist(projects.filter((p) => p.id !== id));
  };

  return (
    <div className="container mx-auto max-w-5xl space-y-6 p-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Projects</h1>
          <p className="text-sm text-muted-foreground">Long-form audiobook & podcast workflows.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button variant="gradient"><Plus className="h-4 w-4" /> New project</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Create project</DialogTitle></DialogHeader>
            <div className="space-y-2">
              <Label htmlFor="ptitle">Title</Label>
              <Input id="ptitle" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Awesome Audiobook" />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
              <Button onClick={create}>Create</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </header>

      {projects.length === 0 ? (
        <div className="flex h-60 flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed text-sm text-muted-foreground">
          <FolderOpen className="h-10 w-10" />
          No projects yet.
        </div>
      ) : (
        <div className="space-y-2">
          {projects.map((p) => (
            <Card key={p.id} className="transition-colors hover:bg-accent/30">
              <CardContent className="p-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="font-semibold">{p.title}</div>
                    <div className="mt-1 text-xs text-muted-foreground">
                      {p.chapters.length} chapters · {new Date(p.createdAt).toLocaleDateString()}
                    </div>
                  </div>
                  <Button size="icon" variant="ghost" onClick={() => void remove(p.id)} aria-label={`Delete ${p.title}`}>
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
