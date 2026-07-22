import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { formatDistanceToNow, parseISO } from 'date-fns';
import {
  Sparkles, Send, Plus, Trash2, Loader2, MessageSquare,
  Target, TrendingDown, TrendingUp, BookOpen, AlertTriangle,
} from 'lucide-react';
import { GlassCard } from '@/components/common/GlassCard';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { MENTOR } from '@/constants/testIds';
import useMentor from '@/hooks/useMentor';

// ---------- Sidebar ----------

function ConversationRow({ convo, active, onSelect, onDelete }) {
  return (
    <div
      role="button"
      tabIndex={0}
      data-testid={`${MENTOR.conversationItem}-${convo.id}`}
      onClick={() => onSelect(convo.id)}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onSelect(convo.id)}
      className={cn(
        'group relative px-3 py-2.5 rounded-xl border cursor-pointer transition-colors',
        active
          ? 'border-primary/40 bg-primary/[0.08]'
          : 'border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04] hover:border-white/[0.12]',
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate">{convo.title || 'New conversation'}</div>
          {convo.last_message_preview && (
            <div className="text-xs text-muted-foreground truncate mt-0.5">
              {convo.last_message_preview}
            </div>
          )}
        </div>
        <button
          data-testid={`${MENTOR.deleteButton}-${convo.id}`}
          onClick={(e) => {
            e.stopPropagation();
            if (window.confirm('Delete this conversation?')) onDelete(convo.id);
          }}
          className="opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 rounded-md hover:bg-rose-500/15 text-rose-300 flex items-center justify-center flex-shrink-0"
          aria-label="Delete conversation"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
      <div className="flex items-center gap-2 mt-1.5">
        <span className="text-[10px] uppercase tracking-wider text-muted-foreground/70">
          {convo.message_count || 0} msgs
        </span>
        <span className="text-[10px] text-muted-foreground/70">·</span>
        <span className="text-[10px] text-muted-foreground/70">
          {(() => {
            try { return formatDistanceToNow(parseISO(convo.updated_at), { addSuffix: true }); }
            catch { return ''; }
          })()}
        </span>
      </div>
    </div>
  );
}

// ---------- Context panel ----------

function ContextPanel({ preview }) {
  if (!preview) return null;
  const { name, target_companies, weak_topics, strong_topics, todays_mission, revision_due_count, current_topic } = preview;
  return (
    <GlassCard className="p-4" data-testid={MENTOR.contextPreview}>
      <div className="flex items-center gap-2 mb-3">
        <span className="h-6 w-6 rounded-md bg-primary/15 border border-primary/30 flex items-center justify-center">
          <Sparkles className="h-3.5 w-3.5 text-primary" />
        </span>
        <div className="text-xs font-mono uppercase tracking-wider text-muted-foreground">Mentor context</div>
      </div>
      <div className="space-y-2.5 text-sm">
        {name && (
          <div>
            <div className="text-xs text-muted-foreground">Learner</div>
            <div className="text-sm">{name}</div>
          </div>
        )}
        {target_companies?.length > 0 && (
          <div>
            <div className="text-xs text-muted-foreground flex items-center gap-1.5"><Target className="h-3 w-3" /> Target companies</div>
            <div className="flex flex-wrap gap-1 mt-1">
              {target_companies.slice(0, 6).map((c) => (
                <Badge key={c} variant="outline" className="text-[10px] font-mono py-0 px-1.5">{c}</Badge>
              ))}
            </div>
          </div>
        )}
        {current_topic && (
          <div>
            <div className="text-xs text-muted-foreground flex items-center gap-1.5"><BookOpen className="h-3 w-3" /> Current topic</div>
            <div className="text-sm mt-0.5">{current_topic.label}</div>
            <div className="text-[10px] text-muted-foreground/80 mt-0.5">
              KB cache: {current_topic.kb_available ? 'available' : 'not generated'}
            </div>
          </div>
        )}
        {weak_topics?.length > 0 && (
          <div>
            <div className="text-xs text-muted-foreground flex items-center gap-1.5"><TrendingDown className="h-3 w-3 text-rose-300" /> Weak areas</div>
            <div className="text-xs text-muted-foreground/90 mt-0.5">{weak_topics.slice(0, 4).join(' · ')}</div>
          </div>
        )}
        {strong_topics?.length > 0 && (
          <div>
            <div className="text-xs text-muted-foreground flex items-center gap-1.5"><TrendingUp className="h-3 w-3 text-emerald-300" /> Strong areas</div>
            <div className="text-xs text-muted-foreground/90 mt-0.5">{strong_topics.slice(0, 4).join(' · ')}</div>
          </div>
        )}
        {todays_mission && (
          <div>
            <div className="text-xs text-muted-foreground">Today's mission</div>
            <div className="text-xs text-muted-foreground/90 mt-0.5">
              {todays_mission.focus_topic || 'general'} · {todays_mission.progress}
            </div>
          </div>
        )}
        {revision_due_count > 0 && (
          <div>
            <div className="text-xs text-muted-foreground">Revision queue</div>
            <div className="text-sm text-amber-300">{revision_due_count} due now</div>
          </div>
        )}
      </div>
    </GlassCard>
  );
}

// ---------- Messages ----------

function MentorMarkdown({ children }) {
  return (
    <div className="prose prose-invert prose-sm max-w-none prose-headings:font-display prose-headings:text-foreground prose-p:text-foreground/90 prose-strong:text-foreground prose-code:text-primary prose-code:bg-primary/10 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:before:content-[''] prose-code:after:content-[''] prose-pre:bg-black/40 prose-pre:border prose-pre:border-white/[0.08] prose-a:text-primary hover:prose-a:text-primary/80 prose-li:text-foreground/90 prose-hr:border-white/[0.08]">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children || ''}</ReactMarkdown>
    </div>
  );
}

function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      data-testid={isUser ? MENTOR.userMessage : MENTOR.assistantMessage}
      className={cn('flex gap-3 py-4', isUser ? 'flex-row-reverse' : 'flex-row')}
    >
      <div className={cn(
        'h-8 w-8 rounded-lg flex-shrink-0 flex items-center justify-center border',
        isUser
          ? 'bg-white/[0.04] border-white/[0.08] text-muted-foreground'
          : 'bg-primary/15 border-primary/30 text-primary',
      )}>
        {isUser ? <MessageSquare className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}
      </div>
      <div className={cn(
        'flex-1 max-w-[85%]',
        isUser && 'flex justify-end',
      )}>
        <div className={cn(
          'rounded-2xl px-4 py-3 border',
          isUser
            ? 'bg-primary/[0.08] border-primary/20 text-foreground'
            : 'bg-white/[0.02] border-white/[0.06]',
        )}>
          {isUser ? (
            <div className="text-sm whitespace-pre-wrap">{message.content}</div>
          ) : (
            <MentorMarkdown>{message.content}</MentorMarkdown>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// ---------- Composer ----------

function Composer({ onSend, sending, disabled }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  const submit = () => {
    if (sending || !text.trim()) return;
    onSend(text);
    setText('');
    // reset auto-grow
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="border-t border-white/[0.06] bg-[hsl(var(--surface))]/60 backdrop-blur-xl px-6 py-4">
      <div className="max-w-4xl mx-auto flex items-end gap-3">
        <Textarea
          ref={textareaRef}
          data-testid={MENTOR.input}
          rows={1}
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            const el = e.target;
            el.style.height = 'auto';
            el.style.height = Math.min(el.scrollHeight, 200) + 'px';
          }}
          onKeyDown={onKeyDown}
          disabled={disabled}
          placeholder="Ask about a concept, request a mock question, or paste your solution for review…"
          className="resize-none bg-white/[0.03] border-white/[0.08] focus:border-primary/40 min-h-[48px] max-h-[200px]"
        />
        <Button
          data-testid={MENTOR.sendButton}
          onClick={submit}
          disabled={sending || !text.trim() || disabled}
          className="h-12 px-5 bg-primary hover:bg-primary/90 text-primary-foreground gap-2"
        >
          {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          <span className="hidden sm:inline">{sending ? 'Thinking…' : 'Send'}</span>
        </Button>
      </div>
      <div className="max-w-4xl mx-auto mt-1.5 text-[10px] text-muted-foreground/70 font-mono uppercase tracking-wider">
        Enter to send · Shift+Enter for newline
      </div>
    </div>
  );
}

// ---------- Empty state ----------

const STARTER_PROMPTS = [
  { title: 'Roadmap next step', body: 'What should I study next based on my current progress?' },
  { title: 'Weak-area drill', body: 'Give me a targeted mini-drill on my weakest topic.' },
  { title: 'Mock interview', body: 'Ask me a system design question at Google L4 bar. Then grade my answer.' },
  { title: 'Explain a topic', body: 'Explain Kadane\'s algorithm and 2 interview follow-ups I should be ready for.' },
];

function EmptyState({ onPick, contextPreview }) {
  return (
    <div className="flex-1 flex items-center justify-center px-6 py-12" data-testid={MENTOR.emptyState}>
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <div className="inline-flex h-12 w-12 rounded-2xl bg-primary/15 border border-primary/30 items-center justify-center mb-4">
            <Sparkles className="h-5 w-5 text-primary" />
          </div>
          <h1 className="font-display text-2xl sm:text-3xl font-semibold tracking-tight">
            PrepOS Mentor
          </h1>
          <p className="mt-2 text-sm text-muted-foreground max-w-md mx-auto">
            A senior interview mentor grounded in your progress, weak areas, and roadmap.
            Not a chatbot — the intelligence layer of PrepOS.
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {STARTER_PROMPTS.map((p) => (
            <button
              key={p.title}
              onClick={() => onPick(p.body)}
              className="text-left p-4 rounded-xl border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04] hover:border-white/[0.12] transition-colors"
            >
              <div className="text-xs font-mono uppercase tracking-wider text-primary/80 mb-1">
                {p.title}
              </div>
              <div className="text-sm text-foreground/90">{p.body}</div>
            </button>
          ))}
        </div>
        {contextPreview && (
          <div className="mt-6 text-center text-[11px] text-muted-foreground/70">
            {contextPreview.weak_topics?.length > 0 && (
              <>Mentor knows your weak areas: {contextPreview.weak_topics.slice(0, 3).join(', ')}</>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ---------- Main page ----------

export default function AIMentor() {
  const m = useMentor();
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [m.messages, m.sending]);

  return (
    <div data-testid={MENTOR.root} className="h-[calc(100vh-64px)] -mx-4 sm:-mx-6 lg:-mx-8 -my-6 flex overflow-hidden">
      {/* Sidebar: history + context */}
      <aside className="hidden md:flex w-[280px] flex-shrink-0 flex-col border-r border-white/[0.06] bg-[hsl(var(--surface))]/40 backdrop-blur-xl">
        <div className="px-4 pt-5 pb-3 border-b border-white/[0.06]">
          <div className="overline mb-2">AI Mentor</div>
          <Button
            data-testid={MENTOR.newChatButton}
            variant="outline"
            className="w-full justify-start gap-2 bg-white/[0.03] border-white/[0.08] hover:bg-white/[0.06]"
            onClick={() => m.startNewChat()}
          >
            <Plus className="h-4 w-4" />
            New chat
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto px-3 py-3 space-y-1.5" data-testid={MENTOR.historyList}>
          {m.historyLoading && (
            <div className="text-xs text-muted-foreground px-2 py-4 text-center">Loading…</div>
          )}
          {!m.historyLoading && m.history.length === 0 && (
            <div className="text-xs text-muted-foreground px-2 py-4 text-center">
              No conversations yet. Start one on the right.
            </div>
          )}
          {m.history.map((c) => (
            <ConversationRow
              key={c.id}
              convo={c}
              active={c.id === m.activeId}
              onSelect={m.loadConversation}
              onDelete={m.removeConversation}
            />
          ))}
        </div>
        <div className="p-3 border-t border-white/[0.06]">
          <ContextPanel preview={m.contextPreview} />
        </div>
      </aside>

      {/* Main chat pane */}
      <main className="flex-1 flex flex-col min-w-0">
        {m.error && (
          <div
            data-testid={MENTOR.errorBanner}
            className="px-6 py-2.5 flex items-center gap-2 bg-rose-500/10 border-b border-rose-500/30 text-rose-200 text-xs"
          >
            <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
            <span className="flex-1">{m.error}</span>
            <button
              onClick={m.dismissError}
              className="text-rose-200/70 hover:text-rose-100 uppercase font-mono tracking-wider text-[10px]"
            >
              Dismiss
            </button>
          </div>
        )}

        {m.messages.length === 0 && !m.sending ? (
          <EmptyState
            onPick={(text) => m.sendMessage(text)}
            contextPreview={m.contextPreview}
          />
        ) : (
          <div
            ref={scrollRef}
            data-testid={MENTOR.messageList}
            className="flex-1 overflow-y-auto"
          >
            <div className="max-w-4xl mx-auto px-6 py-6 divide-y divide-white/[0.04]">
              <AnimatePresence initial={false}>
                {m.messages.map((msg) => (
                  <MessageBubble key={msg.id} message={msg} />
                ))}
              </AnimatePresence>
              {m.sending && (
                <div className="flex gap-3 py-4">
                  <div className="h-8 w-8 rounded-lg bg-primary/15 border border-primary/30 flex items-center justify-center">
                    <Loader2 className="h-4 w-4 text-primary animate-spin" />
                  </div>
                  <div className="rounded-2xl px-4 py-3 border border-white/[0.06] bg-white/[0.02] text-sm text-muted-foreground">
                    Mentor is thinking…
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <Composer onSend={(t) => m.sendMessage(t)} sending={m.sending} />
      </main>
    </div>
  );
}
