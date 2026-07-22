import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Sparkles, X, Send, Wand2, Loader2, AlertTriangle,
  BookOpen, ExternalLink,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAIPanel } from '@/contexts/AIPanelContext';
import { APP_SHELL } from '@/constants/testIds';
import useMentor from '@/hooks/useMentor';
import { MentorLessonCards } from '@/components/mentor/MentorLessonCards';

const SUGGESTED = [
  'What should I study next?',
  'Give me a targeted mini-drill on my weakest topic.',
  'Explain HashMap deeply · Act as Google interviewer',
  'Review my last coding solution.',
];

function DrawerMarkdown({ children }) {
  return (
    <div className="prose prose-invert prose-sm max-w-none prose-headings:font-display prose-headings:text-foreground prose-p:text-foreground/90 prose-code:text-primary prose-code:bg-primary/10 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:before:content-[''] prose-code:after:content-[''] prose-pre:bg-black/40 prose-pre:border prose-pre:border-white/[0.08] prose-a:text-primary prose-li:text-foreground/90">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children || ''}</ReactMarkdown>
    </div>
  );
}

function DrawerMessage({ message }) {
  const isUser = message.role === 'user';
  if (message.style === 'lesson' && message.structured_content) {
    return (
      <div className="py-2">
        <div className="text-[10px] font-mono uppercase tracking-wider text-primary/80 mb-2">Lesson mode</div>
        <MentorLessonCards lesson={message.structured_content} />
      </div>
    );
  }
  return (
    <div className={isUser ? 'flex justify-end' : 'flex justify-start'}>
      <div
        className={
          isUser
            ? 'max-w-[85%] rounded-2xl rounded-tr-md px-4 py-2.5 bg-primary/15 border border-primary/30 text-sm whitespace-pre-wrap'
            : 'max-w-[95%] rounded-2xl rounded-tl-md px-4 py-3 bg-white/[0.03] border border-white/[0.06] text-sm'
        }
      >
        {isUser ? message.content : <DrawerMarkdown>{message.content}</DrawerMarkdown>}
      </div>
    </div>
  );
}

export function AIAssistantPanel() {
  const { open, setOpen } = useAIPanel();
  const [text, setText] = useState('');
  const [lessonMode, setLessonMode] = useState(false);
  const [seedTopicNodeId, setSeedTopicNodeId] = useState(null);
  const scrollRef = useRef(null);
  const navigate = useNavigate();
  const m = useMentor();

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [m.messages, m.sending, open]);

  // Seed prompt hook: other pages can dispatch `mentor:openWithSeed` after
  // stashing `mentor:seedPrompt` (and optionally `mentor:seedTopicNodeId`) in
  // sessionStorage. We pick it up here so the drawer opens pre-filled.
  useEffect(() => {
    const handler = () => {
      const p = window.sessionStorage.getItem('mentor:seedPrompt') || '';
      const nid = window.sessionStorage.getItem('mentor:seedTopicNodeId') || null;
      window.sessionStorage.removeItem('mentor:seedPrompt');
      window.sessionStorage.removeItem('mentor:seedTopicNodeId');
      if (!p) return;
      setText(p);
      setSeedTopicNodeId(nid);
      // If the prompt asked for a structured lesson, auto-enable lesson mode.
      if (/structured lesson|9-card|full lesson|teach me/i.test(p)) setLessonMode(true);
    };
    window.addEventListener('mentor:openWithSeed', handler);
    return () => window.removeEventListener('mentor:openWithSeed', handler);
  }, []);

  const send = () => {
    const val = text.trim();
    if (!val || m.sending) return;
    m.sendMessage(val, {
      responseStyle: lessonMode ? 'lesson' : 'chat',
      topicNodeId: seedTopicNodeId || undefined,
    });
    setText('');
    setSeedTopicNodeId(null);
  };

  const nextStep = m.contextPreview?.recommended_next_step;

  return (
    <AnimatePresence>
      {open && (
        <motion.aside
          initial={{ x: 480, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 480, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 250, damping: 30 }}
          data-testid={APP_SHELL.aiPanel}
          className="fixed top-16 right-0 bottom-0 z-30 w-full sm:w-[480px] border-l border-white/[0.08] bg-[hsl(var(--surface))]/85 backdrop-blur-2xl flex flex-col"
        >
          <div className="h-14 px-5 flex items-center justify-between border-b border-white/[0.06]">
            <div className="flex items-center gap-2">
              <span className="h-7 w-7 rounded-md bg-primary/15 border border-primary/30 flex items-center justify-center">
                <Sparkles className="h-3.5 w-3.5 text-primary" />
              </span>
              <div className="leading-tight">
                <p className="text-sm font-medium">AI Mentor</p>
                <p className="text-[11px] text-muted-foreground font-mono uppercase tracking-wider">
                  {m.sending ? 'thinking…' : 'online'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => { setOpen(false); navigate('/app/ai-mentor'); }}
                className="h-8 px-2.5 flex items-center gap-1.5 text-xs rounded-md border border-white/[0.08] hover:bg-white/[0.04] transition-colors text-muted-foreground hover:text-foreground"
                title="Open full page"
              >
                <ExternalLink className="h-3 w-3" /> Expand
              </button>
              <button
                onClick={() => setOpen(false)}
                className="h-8 w-8 flex items-center justify-center rounded-md border border-white/[0.08] hover:bg-white/[0.04] transition-colors"
                aria-label="Close AI panel"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {m.error && (
            <div className="mx-5 mt-3 px-3 py-2 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-200 text-xs flex items-center gap-2">
              <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
              <span className="flex-1">{m.error}</span>
              <button onClick={m.dismissError} className="text-[10px] font-mono uppercase tracking-wider text-rose-200/70 hover:text-rose-100">Dismiss</button>
            </div>
          )}

          {nextStep && m.messages.length === 0 && (
            <div className="mx-5 mt-3 px-3 py-2.5 rounded-lg border border-primary/25 bg-primary/[0.06]">
              <div className="text-[10px] font-mono uppercase tracking-wider text-primary/80 mb-1">Mentor recommends next</div>
              <div className="text-sm font-medium">{nextStep.label}</div>
              <div className="text-[10px] text-muted-foreground mt-0.5">Based on your prerequisite chain</div>
            </div>
          )}

          <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
            {m.messages.length === 0 && !m.sending && (
              <>
                <div className="rounded-2xl rounded-tl-md px-4 py-3 bg-white/[0.03] border border-white/[0.06] text-sm">
                  I'm your PrepOS Mentor. I know your progress, weak topics, target companies and today's mission — ask me anything and I'll reason from your data.
                </div>
                <div className="pt-2">
                  <div className="overline mb-2">Suggested prompts</div>
                  <div className="flex flex-col gap-2">
                    {SUGGESTED.map((s) => (
                      <button
                        key={s}
                        onClick={() => setText(s)}
                        className="text-left text-sm rounded-lg border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04] px-3 py-2 flex items-center gap-2 transition-colors"
                      >
                        <Wand2 className="h-3.5 w-3.5 text-primary shrink-0" />
                        <span>{s}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}

            {m.messages.map((msg) => (
              <DrawerMessage key={msg.id} message={msg} />
            ))}

            {m.sending && (
              <div className="flex gap-3">
                <div className="h-8 w-8 rounded-lg bg-primary/15 border border-primary/30 flex items-center justify-center">
                  <Loader2 className="h-4 w-4 text-primary animate-spin" />
                </div>
                <div className="rounded-2xl px-4 py-3 border border-white/[0.06] bg-white/[0.02] text-sm text-muted-foreground">
                  Mentor is thinking…
                </div>
              </div>
            )}
          </div>

          <div className="p-4 border-t border-white/[0.06]">
            <div className="flex items-center justify-between mb-2">
              <label className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-wider cursor-pointer text-muted-foreground">
                <input
                  type="checkbox"
                  checked={lessonMode}
                  onChange={(e) => setLessonMode(e.target.checked)}
                  className="h-3 w-3 rounded accent-primary"
                />
                <BookOpen className="h-3 w-3" />
                Structured lesson (9-card)
              </label>
            </div>
            <div className="flex items-end gap-2 rounded-xl border border-white/[0.08] bg-white/[0.02] focus-within:border-primary/50 transition-colors">
              <textarea
                data-testid={APP_SHELL.aiInput}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder={lessonMode ? 'Ask for a full lesson (e.g., "Teach me HashMap")…' : 'Ask the Mentor…'}
                rows={2}
                className="flex-1 resize-none bg-transparent px-3.5 py-2.5 text-sm outline-none placeholder:text-muted-foreground"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    send();
                  }
                }}
              />
              <button
                onClick={send}
                disabled={m.sending || !text.trim()}
                data-testid={APP_SHELL.aiSendButton}
                className="mb-2 mr-2 h-8 w-8 flex items-center justify-center rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-40 transition-colors"
              >
                {m.sending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Send className="h-3.5 w-3.5" />}
              </button>
            </div>
            <p className="mt-2 text-[11px] text-muted-foreground font-mono">
              Grounded in your progress · Enter to send · Shift+Enter for newline
            </p>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
