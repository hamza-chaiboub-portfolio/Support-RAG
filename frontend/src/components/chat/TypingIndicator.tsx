import React from 'react';

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex w-full justify-start mb-4">
      <div className="bg-gray-100 rounded-2xl rounded-bl-none px-4 py-3">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
};
