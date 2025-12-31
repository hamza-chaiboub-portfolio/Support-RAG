import React, { useEffect, useRef } from 'react';
import type { ChatMessage } from '../../types/chat.types';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-2">
      {messages.length === 0 && (
        <div className="flex h-full flex-col items-center justify-center text-gray-400 text-center p-8">
          <p className="text-lg font-medium mb-2">Welcome to SupportRAG</p>
          <p className="text-sm">Ask me anything about our services.</p>
        </div>
      )}
      
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      
      {isLoading && <TypingIndicator />}
      
      <div ref={messagesEndRef} />
    </div>
  );
};
