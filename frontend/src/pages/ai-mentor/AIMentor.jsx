import { Sparkles } from 'lucide-react';
import { PlaceholderPage } from '@/components/common/PlaceholderPage';
export default function AIMentor() {
  return (
    <PlaceholderPage
      overline="AI Mentor"
      title="A senior engineer on call, always."
      description="Ask, review, mock, debug. The Mentor engages your live workspace context in Phase 2."
      icon={Sparkles}
      testId="ai-mentor-root"
    />
  );
}
