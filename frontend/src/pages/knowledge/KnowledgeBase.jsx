import { BookOpen } from 'lucide-react';
import { PlaceholderPage } from '@/components/common/PlaceholderPage';
export default function KnowledgeBase() {
  return (
    <PlaceholderPage
      overline="Knowledge Base"
      title="Your personal engineering encyclopedia."
      description="Curated OS, DBMS, Networks, Java and design notes. Search, revise, and pin."
      icon={BookOpen}
      testId="knowledge-base-root"
    />
  );
}
