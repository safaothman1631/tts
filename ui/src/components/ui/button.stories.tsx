/* Sample Storybook story — typeless to avoid an extra @storybook/react direct dep */
import { Button } from './button';
import { Sparkles } from 'lucide-react';

export default {
  title: 'UI/Button',
  component: Button,
  tags: ['autodocs'],
};

export const Default = { args: { children: 'Click me' } };

export const Gradient = {
  args: {
    variant: 'gradient',
    children: (
      <>
        <Sparkles className="h-4 w-4" /> Synthesize
      </>
    ),
  },
};

export const All = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Button>Default</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="destructive">Destructive</Button>
      <Button variant="gradient">Gradient</Button>
      <Button variant="link">Link</Button>
    </div>
  ),
};
