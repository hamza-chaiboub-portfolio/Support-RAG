import apiClient from './api';
import type { 
  RagQueryRequest, 
  RagQueryResponse, 
  GdprDeleteRequest, 
  GdprDeleteResponse,
  RetrievedChunk
} from '../types/api.types';
import type { ChatMessage, ChatSource } from '../types/chat.types';

// Get project ID from environment
const PROJECT_ID = parseInt(import.meta.env.VITE_PROJECT_ID || '1', 10);

export const chatService = {
  /**
   * Send a message to the RAG system and return formatted ChatMessage
   */
  async sendMessage(query: string, sessionId: string): Promise<ChatMessage> {
    // Only use sessionId if needed, currently unused as per lint
    void sessionId; 
    
    const payload: RagQueryRequest = {
      query,
      project_id: PROJECT_ID,
      // Optional parameters can be added here if needed
      // n_results: 5,
      // threshold: 0.0,
    };
    
    // Call the actual RAG endpoint
    const response = await apiClient.post<RagQueryResponse>('/rag/query', payload);
    const ragResponse = response.data;
    
    // Transform retrieved chunks to ChatSource format
    const sources: ChatSource[] = ragResponse.retrieved_chunks.map((chunk: RetrievedChunk) => {
      // Extract title and URL from metadata if available
      const title = (chunk.metadata?.title as string) || 
                    (chunk.metadata?.filename as string) || 
                    `Document ${chunk.asset_id}`;
                    
      const url = (chunk.metadata?.url as string) || 
                  (chunk.metadata?.source as string) || 
                  '';
                  
      return {
        title,
        url,
        relevance_score: chunk.similarity_score
      };
    });
    
    const chatMessage: ChatMessage = {
      id: `${Date.now()}-${Math.random()}`,
      role: 'assistant',
      content: ragResponse.response,
      timestamp: Date.now(),
      status: 'sent',
      // Map generation_status or other fields if needed, 
      // but confidence_score is removed from response in favor of specific chunk scores
      // We could calculate an average or max confidence if needed, but for now we'll leave it undefined
      // or use the highest chunk score as a proxy if desired.
      // The old API had confidence_score, the new one doesn't at the top level.
      sources: sources,
    };
    
    return chatMessage;
  },

  /**
   * Delete conversation history for GDPR compliance
   */
  async deleteHistory(sessionId: string, reason?: string): Promise<GdprDeleteResponse> {
    const payload: GdprDeleteRequest = {
      session_id: sessionId,
      reason,
    };
    
    // Spec says: /api/v1/gdpr/delete-data
    // Since baseURL includes /api/v1, we just need /gdpr/delete-data
    const response = await apiClient.delete<GdprDeleteResponse>('/gdpr/delete-data', {
      data: payload,
    });
    return response.data;
  }
};
