import { BarChart3 } from 'lucide-react';
import { PlaceholderPage } from '@/components/common/PlaceholderPage';
export default function CommandAnalytics() {
  return (
    <PlaceholderPage
      overline="Command Analytics"
      title="See exactly where your time compounds."
      description="Per-topic velocity, focus quality, mistake patterns and weekly reports. Analytics engine ships in Phase 3."
      icon={BarChart3}
      testId="command-analytics-root"
    />
  );
}
