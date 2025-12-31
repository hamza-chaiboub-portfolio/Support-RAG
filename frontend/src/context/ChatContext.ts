import React, { createContext } from 'react';
import type { ChatState, ChatAction, ChatMessage } from '../types/chat.types';

export interface ChatContextType extends ChatState {
  dispatch: React.Dispatch<ChatAction>;
  addMessage: (message: ChatMessage) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  clearMessages: () => void;
}

export const ChatContext = createContext<ChatContextType | undefined>(undefined);
