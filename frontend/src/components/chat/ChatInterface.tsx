import React from 'react';
import { MessageList } from './MessageList';
import { InputField } from './InputField';
import { AlertBox } from '../common/AlertBox';
import { useChat } from '../../hooks/useChat';
import { chatService } from '../../services/chatService';
import { dataService } from '../../services/dataService';
import { generateUUID } from '../../utils/sessionUtils';
import type { ChatMessage } from '../../types/chat.types';

export const ChatInterface: React.FC = () => {
  const { 
    messages, 
    isLoading, 
    error, 
    sessionId, 
    addMessage, 
    setLoading, 
    setError,
    clearError
  } = useChat();

  const handleSendMessage = async (content: string) => {
    // 1. Add user message
    const userMessage: ChatMessage = {
      id: generateUUID(),
      role: 'user',
      content,
      timestamp: Date.now(),
      status: 'sent'
    };
    addMessage(userMessage);

    // 2. Call API
    setLoading(true);
    try {
      const assistantMessage = await chatService.sendMessage(content, sessionId);
      
      // 3. Add assistant response
      addMessage(assistantMessage);
    } catch (err) {
      // 4. Handle error
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadFile = async (file: File) => {
    setLoading(true);
    clearError();
    
    // Add system message about upload starting
    const startMsg: ChatMessage = {
      id: generateUUID(),
      role: 'system',
      content: `Uploading ${file.name}...`,
      timestamp: Date.now()
    };
    addMessage(startMsg);

    try {
      // 1. Upload
      const uploadRes = await dataService.uploadFile(file);
      
      addMessage({
        id: generateUUID(),
        role: 'system',
        content: `File uploaded. Processing ${file.name}...`,
        timestamp: Date.now()
      });

      // 2. Process
      await dataService.processAsset(uploadRes.asset_id);
      
      addMessage({
        id: generateUUID(),
        role: 'system',
        content: `${file.name} processed and indexed successfully.`,
        timestamp: Date.now()
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload or processing failed');
      addMessage({
        id: generateUUID(),
        role: 'system',
        content: `Failed to process ${file.name}.`,
        timestamp: Date.now()
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
      {error && (
        <AlertBox 
          type="error" 
          message={error} 
          onClose={clearError}
          className="m-4 mb-0"
        />
      )}
      
      <MessageList messages={messages} isLoading={isLoading} />
      
      <InputField 
        onSendMessage={handleSendMessage} 
        onUploadFile={handleUploadFile}
        isLoading={isLoading} 
      />
    </div>
  );
};
