import type { ChatState, ChatAction } from '../types/chat.types';

export const initialChatState: ChatState = {
  messages: [],
  isLoading: false,
  error: null,
  sessionId: '',
};

export function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    case 'CLEAR_MESSAGES':
      return {
        ...state,
        messages: [],
      };
    case 'SET_SESSION_ID':
      return {
        ...state,
        sessionId: action.payload,
      };
    default:
      return state;
  }
}
