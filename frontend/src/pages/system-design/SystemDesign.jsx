import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Network, Layers, Sparkles, Building2, ArrowRight, Loader2,
  BookOpen, Puzzle, ChevronRight, Target,
} from 'lucide-react';
import { GlassCard } from '@/components/common/GlassCard';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useAIPanel } from '@/contexts/AIPanelContext';
import { roadmapService } from '@/services/mission.service';
import { cn } from '@/lib/utils';

/**
 * SystemDesign page — data-driven view of the LLD + HLD tracks from the
 * roadmap engine, plus one-click "Ask the Mentor about this" that opens the
 * top-nav AI panel pre-seeded with the topic.
 *
 * NO static placeholder text. Every card is derived from real roadmap data.
 */

const TRACK_ORDER = ['lld', 'hld'];

function TrackHeader({ track, count, icon: Icon }) {
  return (
    <div className="flex items-center gap-3 mb-4">
      <span className="h-9 w-9 rounded-lg bg-primary/12 border border-primary/25 flex items-center justify-center">
        <Icon className="h-4 w-4 text-primary" />
      </span>
      <div>
        <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
          {track.id === 'lld' ? 'Low-Level Design' : 'High-Level Design'}
        </div>
        <h2 className="font-display text-xl font-semibold tracking-tight">{track.label}</h2>
      </div>
      <Badge variant="outline" className="ml-auto text-[10px] font-mono">{count} topics</Badge>
    </div>
  );
}

function TopicCard({ node, onAskMentor, trackId, moduleId }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <GlassCard className="p-4 h-full flex flex-col">
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="min-w-0">
            <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground truncate">
              {moduleId}
            </div>
            <div className="font-medium text-sm mt-0.5">{node.label}</div>
          </div>
          {node.difficulty && (
            <Badge variant="outline" className={cn(
              'text-[10px] font-mono py-0 px-1.5 shrink-0',
              node.difficulty === 'easy' && 'text-emerald-300 border-emerald-400/30',
              node.difficulty === 'medium' && 'text-amber-300 border-amber-400/30',
              node.difficulty === 'hard' && 'text-rose-300 border-rose-400/30',
            )}>
              {node.difficulty}
            </Badge>
          )}
        </div>
        {node.description && (
          <div className="text-xs text-muted-foreground line-clamp-2 mb-3">{node.description}</div>
        )}
        <div className="mt-auto flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            className="h-8 gap-1.5 text-xs border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.04]"
            asChild
          >
            <Link to={`/app/knowledge-base/nodes/${node.id}`}>
              <BookOpen className="h-3 w-3" /> Open
            </Link>
          </Button>
          <Button
            size="sm"
            className="h-8 gap-1.5 text-xs bg-primary/80 hover:bg-primary/90"
            data-testid={`system-design-ask-mentor-${node.id}`}
            onClick={() => onAskMentor(node)}
          >
            <Sparkles className="h-3 w-3" /> Ask mentor
          </Button>
        </div>
      </GlassCard>
    </motion.div>
  );
}

function ModuleBlock({ mod, onAskMentor }) {
  const topics = mod.children || mod.topics || mod.subtopics || mod.learning_nodes || [];
  const preview = topics.slice(0, 6);
  const [expanded, setExpanded] = useState(false);
  const visible = expanded ? topics : preview;
  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
          <h3 className="text-sm font-mono uppercase tracking-wider text-foreground/90">{mod.label}</h3>
          <span className="text-xs text-muted-foreground">· {topics.length} topics</span>
        </div>
        {topics.length > 6 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-[10px] font-mono uppercase tracking-wider text-primary/80 hover:text-primary"
          >
            {expanded ? 'Show less' : `Show all ${topics.length}`}
          </button>
        )}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {visible.map((t) => (
          <TopicCard key={t.id} node={t} onAskMentor={onAskMentor} trackId={mod.id.split('.')[0]} moduleId={mod.label} />
        ))}
      </div>
    </div>
  );
}

export default function SystemDesign() {
  const { setOpen: setAIOpen } = useAIPanel();
  const [tracks, setTracks] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTrack, setActiveTrack] = useState('lld');

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const data = await roadmapService.tree();
        if (!mounted) return;
        const relevant = (data.tracks || []).filter((t) => TRACK_ORDER.includes(t.id));
        setTracks(relevant);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  const onAskMentor = (node) => {
    // Store a hint the AIAssistantPanel can pick up via URL hash — cheap and
    // decoupled from context wiring. The user still sees the topic name.
    window.sessionStorage.setItem('mentor:seedPrompt', `Teach me ${node.label} as a structured lesson.`);
    window.sessionStorage.setItem('mentor:seedTopicNodeId', node.id);
    window.dispatchEvent(new CustomEvent('mentor:openWithSeed'));
    setAIOpen(true);
  };

  if (loading) {
    return (
      <div className="py-24 flex flex-col items-center gap-3 text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
        <div className="text-xs font-mono uppercase tracking-wider">Loading roadmap…</div>
      </div>
    );
  }

  const current = tracks?.find((t) => t.id === activeTrack);
  const totalTopics = (t) => {
    let count = 0;
    const walk = (nodes) => {
      for (const n of nodes || []) {
        const kind = n.type || n.level;
        if (['topic', 'subtopic', 'node'].includes(kind)) count++;
        walk(n.children || n.modules || n.topics || n.subtopics || n.learning_nodes || []);
      }
    };
    walk(t?.children || t?.modules || []);
    return count;
  };

  return (
    <div data-testid="system-design-root" className="space-y-6">
      {/* Hero */}
      <div className="flex items-start gap-4">
        <span className="h-11 w-11 rounded-xl bg-primary/12 border border-primary/25 flex items-center justify-center">
          <Network className="h-5 w-5 text-primary" />
        </span>
        <div className="flex-1">
          <div className="overline">System Design</div>
          <h1 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight mt-1">
            LLD and HLD, taught the way senior engineers think.
          </h1>
          <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
            Every topic here is roadmap-anchored — click "Ask mentor" on any card to open a
            structured 9-card lesson grounded in your current progress, weak areas and target companies.
          </p>
        </div>
      </div>

      {/* Track toggle */}
      <div className="flex gap-2">
        {tracks?.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTrack(t.id)}
            className={cn(
              'px-4 py-2 rounded-lg border text-sm font-medium transition-colors',
              activeTrack === t.id
                ? 'border-primary/40 bg-primary/[0.08] text-foreground'
                : 'border-white/[0.06] bg-white/[0.02] text-muted-foreground hover:text-foreground hover:bg-white/[0.04]',
            )}
          >
            {t.id === 'lld' ? 'LLD Roadmap' : 'HLD Roadmap'}
            <span className="ml-2 text-xs opacity-70">{totalTopics(t)}</span>
          </button>
        ))}
      </div>

      {current && (
        <div>
          <TrackHeader track={current} count={totalTopics(current)} icon={current.id === 'lld' ? Layers : Puzzle} />
          {(current.children || current.modules || []).map((mod) => (
            <ModuleBlock key={mod.id} mod={mod} onAskMentor={onAskMentor} />
          ))}
        </div>
      )}

      {/* Company design signals */}
      <GlassCard className="p-5">
        <div className="flex items-center gap-2 mb-3">
          <Building2 className="h-4 w-4 text-primary" />
          <h3 className="font-display text-base font-semibold tracking-tight">Company-specific design discussions</h3>
        </div>
        <p className="text-sm text-muted-foreground mb-3">
          Ask the mentor to run a mock design interview at a specific company bar. It will use the
          company's known signals (scale, latency, data models) and your progress.
        </p>
        <div className="flex flex-wrap gap-2">
          {['Google', 'Meta', 'Amazon', 'Microsoft', 'Uber', 'Atlassian'].map((c) => (
            <Button
              key={c}
              size="sm"
              variant="outline"
              className="h-8 gap-1.5 text-xs border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.04]"
              onClick={() => {
                window.sessionStorage.setItem('mentor:seedPrompt', `Act as a Senior ${c} interviewer and run a mock system design round with me. Grade my answer.`);
                window.sessionStorage.removeItem('mentor:seedTopicNodeId');
                window.dispatchEvent(new CustomEvent('mentor:openWithSeed'));
                setAIOpen(true);
              }}
            >
              <Target className="h-3 w-3" /> Mock @ {c}
            </Button>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
