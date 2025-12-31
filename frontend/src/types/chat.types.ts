export interface ChatSource {
  title: string;
  url: string;
  relevance_score: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  status?: 'sending' | 'sent' | 'error';
  sources?: ChatSource[];
  confidence_score?: number;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sessionId: string;
}

export type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_ERROR' }
  | { type: 'CLEAR_MESSAGES' }
  | { type: 'SET_SESSION_ID'; payload: string };
