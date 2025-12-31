import { useReducer, useEffect, type ReactNode } from 'react';
import { chatReducer, initialChatState } from './chatReducer';
import { useSession } from '../hooks/useSession';
import { ChatContext, type ChatContextType } from './ChatContext';
import type { ChatMessage } from '../types/chat.types';

export function ChatProvider({ children }: { children: ReactNode }) {
  const { sessionId } = useSession();
  const [state, dispatch] = useReducer(chatReducer, {
    ...initialChatState,
    sessionId,
  });

  // Sync session ID from hook to state
  useEffect(() => {
    if (sessionId && sessionId !== state.sessionId) {
      dispatch({ type: 'SET_SESSION_ID', payload: sessionId });
    }
  }, [sessionId, state.sessionId]);

  const addMessage = (message: ChatMessage) => {
    dispatch({ type: 'ADD_MESSAGE', payload: message });
  };

  const setLoading = (isLoading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: isLoading });
  };

  const setError = (error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const clearMessages = () => {
    dispatch({ type: 'CLEAR_MESSAGES' });
  };

  const value: ChatContextType = {
    ...state,
    dispatch,
    addMessage,
    setLoading,
    setError,
    clearError,
    clearMessages,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}
