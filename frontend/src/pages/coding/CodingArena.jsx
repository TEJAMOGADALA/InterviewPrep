import { Code2 } from 'lucide-react';
import { PlaceholderPage } from '@/components/common/PlaceholderPage';
export default function CodingArena() {
  return (
    <PlaceholderPage
      overline="Coding Arena"
      title="Curated coding practice, adaptive to you."
      description="Structured DSA sprints, contest simulators and interview-style problems calibrated by your skill baseline."
      icon={Code2}
      testId="coding-arena-root"
    />
  );
}
