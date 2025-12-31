import React from 'react';
import type { ChatMessage } from '../../types/chat.types';
import { SourceCitation } from './SourceCitation';

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
  
  if (isSystem) {
    return (
      <div className="flex w-full justify-center mb-4">
        <div className="bg-gray-100 text-gray-600 px-4 py-1 rounded-full text-xs font-medium">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={isUser ? 'message-user' : 'message-assistant'}>
        <div className="whitespace-pre-wrap">{message.content}</div>
        <div className={`text-xs mt-1 ${isUser ? 'text-sky-100' : 'text-gray-500'}`}>
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
        {!isUser && (
          <SourceCitation 
            sources={message.sources} 
            confidence_score={message.confidence_score}
          />
        )}
      </div>
    </div>
  );
};
