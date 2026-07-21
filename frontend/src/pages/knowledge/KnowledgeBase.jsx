import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import {
  BookOpen, Loader2, ChevronRight, Search, Layers, Cpu,
  Coffee, Network, Database, Wifi, Code2, Hammer, MessageCircle, FileText,
} from 'lucide-react';
import { GlassCard } from '@/components/common/GlassCard';
import { formatApiError } from '@/utils/formatApiError';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { StatusBadge } from '@/components/progress/StatusBadge';
import { FilterChips } from '@/components/progress/FilterChips';
import { useProgressTree, matchNode } from '@/hooks/useProgressTree';

const TRACK_ICON = {
  dsa: Code2, java: Coffee, lld: Layers, hld: Network,
  operating_systems: Cpu, dbms: Database, computer_networks: Wifi,
  projects: Hammer, behavioral: MessageCircle, resume: FileText,
};

const BUCKET_DOT = {
  green: 'bg-emerald-400',
  yellow: 'bg-amber-400',
  red: 'bg-rose-400',
};

function flattenTopics(rootNodes, expanded) {
  const out = [];
  // Iterative DFS via explicit stack — no recursion so the visual-edit
  // babel plugin cannot blow its call stack while traversing.
  const stack = [];
  for (let i = rootNodes.length - 1; i >= 0; i--) {
    stack.push({ n: rootNodes[i], depth: 0 });
  }
  while (stack.length) {
    const { n, depth } = stack.pop();
    const hasKids = (n.children || []).length > 0;
    out.push({ node: n, depth, hasKids });
    if (hasKids && expanded.has(n.id)) {
      for (let i = n.children.length - 1; i >= 0; i--) {
        stack.push({ n: n.children[i], depth: depth + 1 });
      }
    }
  }
  return out;
}

function TopicItem({ topic, depth, hasKids, isOpen, onToggle }) {
  const status = topic.progress?.status || 'not_started';
  const bkt = topic.progress?.revision_bucket || 'green';
  const bookmarked = !!topic.progress?.bookmarked;
  const favorite = !!topic.progress?.favorite;
  return (
    <div style={{ paddingLeft: `${depth * 20}px` }}>
      <div className="flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-white/[0.03] transition-colors">
        {hasKids ? (
          <button onClick={onToggle} className="shrink-0 h-5 w-5 flex items-center justify-center rounded hover:bg-white/[0.05]">
            <ChevronRight className={cn('h-3 w-3 text-muted-foreground transition-transform', isOpen && 'rotate-90')} />
          </button>
        ) : (
          <span className="h-5 w-5 shrink-0 flex items-center justify-center">
            <span className={cn('h-1.5 w-1.5 rounded-full', BUCKET_DOT[bkt])} />
          </span>
        )}
        <Link
          to={`/app/knowledge-base/nodes/${topic.id}`}
          data-testid={`roadmap-node-${topic.id}`}
          className="flex-1 text-sm truncate hover:text-primary transition-colors"
        >
          {topic.label}
        </Link>
        {bookmarked && (
          <span title="Bookmarked" className="text-primary text-[10px]" data-testid={`node-bookmark-indicator-${topic.id}`}>■</span>
        )}
        {favorite && (
          <span title="Favorite" className="text-amber-300 text-[10px]" data-testid={`node-favorite-indicator-${topic.id}`}>★</span>
        )}
        <StatusBadge status={status} className="hidden sm:inline-block" />
        <span className="font-mono text-[11px] text-muted-foreground w-10 text-right">
          {Math.round(topic.progress?.mastery_percentage || 0)}%
        </span>
      </div>
    </div>
  );
}

function ModuleBlock({ module, isOpen, onToggle, expanded, toggleNode }) {
  const modMastery = module.progress?.mastery_percentage || 0;
  const rows = isOpen ? flattenTopics(module.children || [], expanded) : [];
  return (
    <div className="rounded-lg border border-white/[0.06] bg-white/[0.02]" data-testid={`roadmap-module-${module.id}`}>
      <button
        onClick={onToggle}
        className="w-full text-left px-4 py-3 flex items-center gap-3 hover:bg-white/[0.03] transition-colors"
      >
        <ChevronRight className={cn('h-3.5 w-3.5 text-muted-foreground shrink-0 transition-transform', isOpen && 'rotate-90')} />
        <span className="flex-1 text-sm font-medium">{module.label}</span>
        <div className="w-32 h-1 rounded-full bg-white/[0.05] overflow-hidden hidden sm:block">
          <div className="h-full bg-primary/70" style={{ width: `${modMastery}%` }} />
        </div>
        <span className="font-mono text-[11px] text-muted-foreground w-10 text-right">
          {Math.round(modMastery)}%
        </span>
      </button>
      {isOpen && (
        <div className="px-4 pb-3 pt-1 space-y-1">
          {rows.map((r) => (
            <TopicItem
              key={r.node.id} topic={r.node} depth={r.depth} hasKids={r.hasKids}
              isOpen={expanded.has(r.node.id)}
              onToggle={() => toggleNode(r.node.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function TrackBlock({ track, isOpen, onToggle, expanded, toggleNode }) {
  const Icon = TRACK_ICON[track.id] || BookOpen;
  const mastery = track.progress?.mastery_percentage || 0;
  const bucket = track.progress?.revision_bucket || 'green';
  const modules = track.children || [];
  return (
    <GlassCard className="p-0 overflow-hidden" data-testid={`roadmap-track-${track.id}`}>
      <button
        onClick={onToggle}
        className="w-full text-left px-6 py-5 flex items-center gap-4 hover:bg-white/[0.02] transition-colors"
      >
        <span className="h-10 w-10 rounded-xl bg-primary/15 border border-primary/30 flex items-center justify-center shrink-0">
          <Icon className="h-5 w-5 text-primary" />
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h2 className="font-display text-lg font-semibold tracking-tight">{track.label}</h2>
            <span className={cn('h-1.5 w-1.5 rounded-full', BUCKET_DOT[bucket])} />
          </div>
          <div className="mt-2 flex items-center gap-3">
            <div className="h-1.5 flex-1 rounded-full bg-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-primary to-secondary" style={{ width: `${mastery}%` }} />
            </div>
            <span className="font-mono text-xs text-muted-foreground w-14 text-right">
              {Math.round(mastery)}%
            </span>
          </div>
        </div>
        <ChevronRight className={cn('h-4 w-4 text-muted-foreground shrink-0 transition-transform', isOpen && 'rotate-90')} />
      </button>
      {isOpen && (
        <div className="px-6 pb-5 pt-1 space-y-2">
          {modules.map((m) => (
            <ModuleBlock
              key={m.id} module={m}
              isOpen={expanded.has(m.id)}
              onToggle={() => toggleNode(m.id)}
              expanded={expanded}
              toggleNode={toggleNode}
            />
          ))}
        </div>
      )}
    </GlassCard>
  );
}

export default function KnowledgeBase() {
  const { tree, loading, error } = useProgressTree();
  const [expanded, setExpanded] = useState(new Set());
  const [q, setQ] = useState('');
  const [filters, setFilters] = useState(new Set());

  useEffect(() => {
    if (error) toast.error(formatApiError(error));
  }, [error]);

  const toggleNode = (id) => {
    setExpanded((s) => {
      const n = new Set(s);
      n.has(id) ? n.delete(id) : n.add(id);
      return n;
    });
  };

  const toggleFilter = (key) => {
    setFilters((s) => {
      const n = new Set(s);
      n.has(key) ? n.delete(key) : n.add(key);
      return n;
    });
  };

  const clearFilters = () => setFilters(new Set());

  const filteredTracks = useMemo(() => {
    if (!tree) return [];
    const needle = q.trim().toLowerCase();
    const hasFilters = filters.size > 0;
    if (!needle && !hasFilters) return tree.tracks || [];
    // Iterative filter — walk with an explicit stack so the visual-edit
    // plugin cannot re-enter itself while analysing this closure.
    const autoExpand = new Set();
    const cloneMatches = (root) => {
      // Post-order iterative: mark matches from leaves up.
      const stack = [{ node: root, phase: 'enter', copy: null, parentCopy: null }];
      const rootBox = { copy: null };
      const parentBoxByNodeId = new Map();
      parentBoxByNodeId.set(root, rootBox);
      const kidsCollected = new Map();
      while (stack.length) {
        const it = stack[stack.length - 1];
        if (it.phase === 'enter') {
          it.phase = 'exit';
          kidsCollected.set(it.node, []);
          const children = it.node.children || [];
          for (let i = children.length - 1; i >= 0; i--) {
            stack.push({ node: children[i], phase: 'enter', parent: it.node });
          }
        } else {
          stack.pop();
          const kids = kidsCollected.get(it.node) || [];
          const textMatch = !needle
            || it.node.label.toLowerCase().includes(needle)
            || (it.node.id || '').includes(needle);
          const filterMatch = !hasFilters || matchNode(it.node, filters);
          const selfMatch = textMatch && filterMatch;
          if (selfMatch || kids.length) {
            const copy = { ...it.node, children: kids };
            if (kids.length) autoExpand.add(it.node.id);
            if (it.parent) {
              (kidsCollected.get(it.parent) || []).push(copy);
            } else {
              rootBox.copy = copy;
            }
          }
        }
      }
      return rootBox.copy;
    };
    const tracks = (tree.tracks || []).map(cloneMatches).filter(Boolean);
    setTimeout(() => setExpanded((s) => new Set([...s, ...autoExpand])), 0);
    return tracks;
  }, [tree, q, filters]);

  if (loading || !tree) {
    return (
      <div className="py-24 flex flex-col items-center gap-3 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span className="overline">Loading roadmap</span>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="knowledge-base-root">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <div className="overline mb-2">Knowledge Explorer</div>
          <h1 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight">
            The Master Roadmap
          </h1>
          <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
            One versioned source of truth for every topic, node and interview signal.
            Click a domain to drill down. Everything else in PrepOS derives from this.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono text-muted-foreground">
          <span>Version <span className="text-primary">{tree.version}</span></span>
          <span>·</span>
          <span>{filteredTracks.length} tracks</span>
        </div>
      </div>

      <div className="relative max-w-lg">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Find a topic, pattern or learning node…"
          data-testid="knowledge-search-input"
          className="pl-10 bg-white/[0.03] border-white/10 h-11"
        />
      </div>

      <FilterChips
        active={filters}
        companies={tree.companies || []}
        onToggle={toggleFilter}
        onClear={clearFilters}
      />

      <div className="grid grid-cols-1 gap-4">
        {filteredTracks.map((track) => (
          <TrackBlock
            key={track.id} track={track}
            isOpen={expanded.has(track.id)}
            onToggle={() => toggleNode(track.id)}
            expanded={expanded}
            toggleNode={toggleNode}
          />
        ))}
      </div>
    </div>
  );
}
