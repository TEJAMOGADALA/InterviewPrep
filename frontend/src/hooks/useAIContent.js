import { useCallback, useEffect, useRef, useState } from 'react';
import { toast } from 'sonner';
import { roadmapService } from '@/services/mission.service';
import { formatApiError } from '@/utils/formatApiError';

/**
 * Shared fetch hook for AI-generated knowledge content.
 *
 * Both the top summary cards (Interview Tips / Common Mistakes) and the
 * tabbed viewer read from this hook — one HTTP call per node visit.
 *
 * In-memory cache keyed by nodeId prevents duplicate GETs when multiple
 * consumers mount in the same render (StrictMode double-invoke safe).
 */
const inflight = new Map(); // nodeId -> Promise
const cache = new Map();    // nodeId -> latest content payload

export function useAIContent(nodeId) {
  const [content, setContent] = useState(() => cache.get(nodeId) || null);
  const [loading, setLoading] = useState(!cache.has(nodeId));
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState(null);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; };
  }, []);

  const fetchContent = useCallback(async () => {
    if (!nodeId) return;
    setLoading(true);
    let p = inflight.get(nodeId);
    if (!p) {
      p = roadmapService.getContent(nodeId).finally(() => inflight.delete(nodeId));
      inflight.set(nodeId, p);
    }
    try {
      const c = await p;
      cache.set(nodeId, c);
      if (mounted.current) setContent(c);
    } catch (e) {
      if (mounted.current) toast.error(formatApiError(e));
    } finally {
      if (mounted.current) setLoading(false);
    }
  }, [nodeId]);

  useEffect(() => { fetchContent(); }, [fetchContent]);

  const generate = useCallback(async ({ regenerate = false } = {}) => {
    if (!nodeId || generating) return;
    setGenerating(true);
    setGenError(null);
    try {
      const c = regenerate
        ? await roadmapService.regenerateContent(nodeId)
        : await roadmapService.generateContent(nodeId);
      cache.set(nodeId, c);
      if (mounted.current) setContent(c);
      toast.success(regenerate ? 'Content regenerated.' : 'Content ready.');
    } catch (e) {
      const detail = e?.response?.data?.detail;
      const err = {
        kind: detail?.error || 'unknown',
        message: detail?.message || formatApiError(e),
      };
      if (mounted.current) setGenError(err);
      toast.error(err.message);
    } finally {
      if (mounted.current) setGenerating(false);
    }
  }, [nodeId, generating]);

  return { content, loading, generating, genError, generate, refresh: fetchContent };
}
