import { useCallback, useEffect, useMemo, useState } from 'react';
import api from '@/services/api';

/**
 * useMentor — the single React hook that drives the AI Mentor page.
 *
 * Responsibilities:
 *   • Load conversation history sidebar.
 *   • Load a single conversation transcript when selected.
 *   • Send a message (creates a conversation on demand) and merge the reply.
 *   • Delete a conversation.
 *   • Surface loading / error states without swallowing them.
 *
 * The backend is authoritative — every write refetches the affected slice so
 * the UI never gets out of sync with Mongo.
 */
export function useMentor() {
  const [history, setHistory] = useState([]);            // sidebar items
  const [historyLoading, setHistoryLoading] = useState(false);

  const [activeId, setActiveId] = useState(null);        // selected conversation id
  const [messages, setMessages] = useState([]);          // active thread
  const [conversation, setConversation] = useState(null);

  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [contextPreview, setContextPreview] = useState(null);

  const refreshHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const { data } = await api.get('/mentor/history');
      setHistory(Array.isArray(data) ? data : []);
    } catch (e) {
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  const loadConversation = useCallback(async (id) => {
    if (!id) {
      setActiveId(null);
      setMessages([]);
      setConversation(null);
      return;
    }
    setError(null);
    try {
      const { data } = await api.get(`/mentor/conversation/${id}`);
      setActiveId(id);
      setConversation(data.conversation);
      setMessages(data.messages || []);
    } catch (e) {
      setError(e?.response?.data?.detail?.message || 'Failed to load conversation.');
    }
  }, []);

  const startNewChat = useCallback(async ({ topicNodeId } = {}) => {
    setError(null);
    setActiveId(null);
    setMessages([]);
    setConversation(null);
    setContextPreview(null);
    if (topicNodeId) {
      // Pre-create so the sidebar shows it immediately.
      try {
        const { data } = await api.post('/mentor/new-chat', {
          topic_node_id: topicNodeId,
        });
        await refreshHistory();
        setActiveId(data.id);
        setConversation(data);
      } catch (e) {
        // Non-fatal — user can still type a message.
      }
    }
  }, [refreshHistory]);

  const sendMessage = useCallback(async (text, { topicNodeId } = {}) => {
    const trimmed = (text || '').trim();
    if (!trimmed) return;
    setSending(true);
    setError(null);
    // Optimistic user turn — swapped for the persisted row after the API responds.
    const optimisticId = `optimistic-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: optimisticId,
        conversation_id: activeId || 'pending',
        role: 'user',
        content: trimmed,
        created_at: new Date().toISOString(),
        __optimistic: true,
      },
    ]);
    try {
      const { data } = await api.post('/mentor/chat', {
        message: trimmed,
        conversation_id: activeId || undefined,
        topic_node_id: topicNodeId || undefined,
      });
      setActiveId(data.conversation_id);
      setConversation(data.conversation);
      setContextPreview(data.context_summary || null);
      // Replace the optimistic row with the persisted user + assistant messages.
      setMessages((prev) => {
        const withoutOptimistic = prev.filter((m) => m.id !== optimisticId);
        return [...withoutOptimistic, data.user_message, data.message];
      });
      // Keep sidebar fresh (title / preview / order).
      refreshHistory();
    } catch (e) {
      setMessages((prev) => prev.filter((m) => m.id !== optimisticId));
      const detail = e?.response?.data?.detail;
      const message = typeof detail === 'string'
        ? detail
        : detail?.message || 'Mentor is temporarily unreachable.';
      setError(message);
    } finally {
      setSending(false);
    }
  }, [activeId, refreshHistory]);

  const removeConversation = useCallback(async (id) => {
    try {
      await api.delete(`/mentor/conversation/${id}`);
      if (id === activeId) {
        setActiveId(null);
        setMessages([]);
        setConversation(null);
      }
      await refreshHistory();
    } catch (e) {
      setError(e?.response?.data?.detail?.message || 'Failed to delete conversation.');
    }
  }, [activeId, refreshHistory]);

  useEffect(() => {
    refreshHistory();
    // Pull an initial context preview so the "Mentor knows about you" card is
    // never empty on first paint.
    api.get('/mentor/context/preview').then(({ data }) => {
      setContextPreview(data);
    }).catch(() => {});
  }, [refreshHistory]);

  return useMemo(() => ({
    history,
    historyLoading,
    activeId,
    conversation,
    messages,
    sending,
    error,
    contextPreview,
    // actions
    refreshHistory,
    loadConversation,
    startNewChat,
    sendMessage,
    removeConversation,
    dismissError: () => setError(null),
  }), [
    history, historyLoading, activeId, conversation, messages,
    sending, error, contextPreview,
    refreshHistory, loadConversation, startNewChat, sendMessage, removeConversation,
  ]);
}

export default useMentor;
