import { Network } from 'lucide-react';
import { PlaceholderPage } from '@/components/common/PlaceholderPage';
export default function SystemDesign() {
  return (
    <PlaceholderPage
      overline="System Design"
      title="LLD and HLD, taught the way senior engineers think."
      description="Case studies, diagrams and interactive design canvas. Powered by the Design Engine, arriving in Phase 2."
      icon={Network}
      testId="system-design-root"
    />
  );
}
