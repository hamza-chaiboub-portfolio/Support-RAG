import { chatService } from '../../../src/services/chatService';
import apiClient from '../../../src/services/api';
import type { RagQueryResponse } from '../../../src/types/api.types';

vi.mock('../../../src/services/api', () => ({
  default: {
    post: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('Chat Service', () => {
  const mockSessionId = 'test-session-123';
  const mockQuery = 'What is your return policy?';
  const mockProjectId = 1;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('sendMessage', () => {
    it('should send message and return ChatMessage with sources mapped from chunks', async () => {
      const mockResponse: RagQueryResponse = {
        status: 'success',
        project_id: mockProjectId,
        query: mockQuery,
        retrieved_chunks: [
          {
            chunk_id: 1,
            asset_id: 101,
            content: 'Chunk content 1',
            similarity_score: 0.95,
            metadata: {
              title: 'Return Policy Guide',
              url: 'https://example.com/returns'
            }
          },
          {
            chunk_id: 2,
            asset_id: 102,
            content: 'Chunk content 2',
            similarity_score: 0.87,
            metadata: {
              filename: 'FAQ.pdf',
              source: 'https://example.com/faq'
            }
          }
        ],
        retrieved_count: 2,
        response: 'Our return policy allows returns within 30 days.',
        generation_status: 'success'
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const result = await chatService.sendMessage(mockQuery, mockSessionId);

      expect(apiClient.post).toHaveBeenCalledTimes(1);
      expect(apiClient.post).toHaveBeenCalledWith('/rag/query', {
        query: mockQuery,
        project_id: mockProjectId,
      });

      expect(result).toMatchObject({
        role: 'assistant',
        content: mockResponse.response,
        status: 'sent',
      });
      
      expect(result.sources).toHaveLength(2);
      expect(result.sources?.[0]).toEqual({
        title: 'Return Policy Guide',
        url: 'https://example.com/returns',
        relevance_score: 0.95
      });
      expect(result.sources?.[1]).toEqual({
        title: 'FAQ.pdf',
        url: 'https://example.com/faq',
        relevance_score: 0.87
      });

      expect(result.id).toBeDefined();
      expect(result.timestamp).toBeDefined();
    });

    it('should handle response without chunks', async () => {
      const mockResponse: RagQueryResponse = {
        status: 'success',
        project_id: mockProjectId,
        query: mockQuery,
        retrieved_chunks: [],
        retrieved_count: 0,
        response: 'I am not sure about this topic.',
        generation_status: 'success'
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const result = await chatService.sendMessage(mockQuery, mockSessionId);

      expect(result).toMatchObject({
        role: 'assistant',
        content: mockResponse.response,
        status: 'sent',
      });
      expect(result.sources).toEqual([]);
    });
    
    it('should handle chunks with missing metadata gracefully', async () => {
      const mockResponse: RagQueryResponse = {
        status: 'success',
        project_id: mockProjectId,
        query: mockQuery,
        retrieved_chunks: [
          {
            chunk_id: 10,
            asset_id: 500,
            content: 'Content',
            similarity_score: 0.8,
            metadata: {}
          }
        ],
        retrieved_count: 1,
        response: 'Answer',
        generation_status: 'success'
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const result = await chatService.sendMessage(mockQuery, mockSessionId);

      expect(result.sources?.[0]).toEqual({
        title: 'Document 500', // Fallback
        url: '', // Fallback
        relevance_score: 0.8
      });
    });

    it('should propagate API errors', async () => {
      const mockError = new Error('API request failed');
      vi.mocked(apiClient.post).mockRejectedValue(mockError);

      await expect(chatService.sendMessage(mockQuery, mockSessionId))
        .rejects
        .toThrow('API request failed');
    });

    it('should generate unique message IDs', async () => {
      const mockResponse: RagQueryResponse = {
        status: 'success',
        project_id: mockProjectId,
        query: mockQuery,
        retrieved_chunks: [],
        retrieved_count: 0,
        response: 'Test response',
        generation_status: 'success'
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const result1 = await chatService.sendMessage(mockQuery, mockSessionId);
      const result2 = await chatService.sendMessage(mockQuery, mockSessionId);

      expect(result1.id).not.toBe(result2.id);
    });
  });

  describe('deleteHistory', () => {
    it('should call delete endpoint with session ID and reason', async () => {
      const mockReason = 'User requested deletion';
      const mockResponse = {
        data: {
          message: 'History deleted successfully',
          status: 'success' as const,
        },
      };

      vi.mocked(apiClient.delete).mockResolvedValue(mockResponse);

      const result = await chatService.deleteHistory(mockSessionId, mockReason);

      expect(apiClient.delete).toHaveBeenCalledTimes(1);
      expect(apiClient.delete).toHaveBeenCalledWith('/gdpr/delete-data', {
        data: {
          session_id: mockSessionId,
          reason: mockReason,
        },
      });

      expect(result).toEqual(mockResponse.data);
    });

    it('should call delete endpoint without reason', async () => {
      const mockResponse = {
        data: {
          message: 'History deleted successfully',
          status: 'success' as const,
        },
      };

      vi.mocked(apiClient.delete).mockResolvedValue(mockResponse);

      const result = await chatService.deleteHistory(mockSessionId);

      expect(apiClient.delete).toHaveBeenCalledTimes(1);
      expect(apiClient.delete).toHaveBeenCalledWith('/gdpr/delete-data', {
        data: {
          session_id: mockSessionId,
          reason: undefined,
        },
      });

      expect(result).toEqual(mockResponse.data);
    });

    it('should propagate delete errors', async () => {
      const mockError = new Error('Delete failed');
      vi.mocked(apiClient.delete).mockRejectedValue(mockError);

      await expect(chatService.deleteHistory(mockSessionId))
        .rejects
        .toThrow('Delete failed');
    });
  });
});
