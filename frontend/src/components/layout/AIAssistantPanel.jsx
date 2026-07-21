import { AnimatePresence, motion } from 'framer-motion';
import { Sparkles, X, Send, Wand2 } from 'lucide-react';
import { useState } from 'react';
import { useAIPanel } from '@/contexts/AIPanelContext';
import { APP_SHELL } from '@/constants/testIds';

const SUGGESTED = [
  'Explain LRU cache with a Java implementation',
  'Design a rate limiter for a payments API',
  'Give me 3 medium DSA questions on graphs',
  'Mock interview me for SDE-2 at Google',
];

export function AIAssistantPanel() {
  const { open, setOpen } = useAIPanel();
  const [text, setText] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "I'm your PrepOS Mentor. I'll be online in the next drop — for now you can browse suggested prompts on the right.",
    },
  ]);

  const send = () => {
    if (!text.trim()) return;
    setMessages((m) => [
      ...m,
      { role: 'user', content: text },
      {
        role: 'assistant',
        content:
          "AI is not yet wired up in this foundation build. Your prompt has been captured — it'll be routed to the Mentor engine in Phase 2.",
      },
    ]);
    setText('');
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.aside
          initial={{ x: 420, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 420, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 250, damping: 30 }}
          data-testid={APP_SHELL.aiPanel}
          className="fixed top-16 right-0 bottom-0 z-30 w-full sm:w-[420px] border-l border-white/[0.08] bg-[hsl(var(--surface))]/85 backdrop-blur-2xl flex flex-col"
        >
          <div className="h-14 px-5 flex items-center justify-between border-b border-white/[0.06]">
            <div className="flex items-center gap-2">
              <span className="h-7 w-7 rounded-md bg-primary/15 border border-primary/30 flex items-center justify-center">
                <Sparkles className="h-3.5 w-3.5 text-primary" />
              </span>
              <div className="leading-tight">
                <p className="text-sm font-medium">AI Mentor</p>
                <p className="text-[11px] text-muted-foreground font-mono uppercase tracking-wider">docked · beta</p>
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="h-8 w-8 flex items-center justify-center rounded-md border border-white/[0.08] hover:bg-white/[0.04] transition-colors"
              aria-label="Close AI panel"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-5 py-5 space-y-4">
            {messages.map((m, i) => (
              <div
                key={i}
                className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}
              >
                <div
                  className={
                    m.role === 'user'
                      ? 'max-w-[85%] rounded-2xl rounded-tr-md px-4 py-2.5 bg-primary/15 border border-primary/30 text-sm'
                      : 'max-w-[85%] rounded-2xl rounded-tl-md px-4 py-2.5 bg-white/[0.03] border border-white/[0.06] text-sm text-foreground/90'
                  }
                >
                  {m.content}
                </div>
              </div>
            ))}

            <div className="pt-4">
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
          </div>

          <div className="p-4 border-t border-white/[0.06]">
            <div className="flex items-end gap-2 rounded-xl border border-white/[0.08] bg-white/[0.02] focus-within:border-primary/50 transition-colors">
              <textarea
                data-testid={APP_SHELL.aiInput}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Ask the Mentor…"
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
                data-testid={APP_SHELL.aiSendButton}
                className="mb-2 mr-2 h-8 w-8 flex items-center justify-center rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                <Send className="h-3.5 w-3.5" />
              </button>
            </div>
            <p className="mt-2 text-[11px] text-muted-foreground font-mono">
              Mentor engine offline · Phase 2
            </p>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
