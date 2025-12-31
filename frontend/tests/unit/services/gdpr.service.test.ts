import { gdprService } from '../../../src/services/gdpr.service';
import apiClient from '../../../src/services/api';

// Mock the API client
vi.mock('../../../src/services/api', () => ({
  default: {
    post: vi.fn(),
  },
}));

describe('GDPR Service', () => {
  const mockSessionId = 'test-session-id';
  const mockReason = 'privacy concerns';

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call delete endpoint with correct parameters including reason', async () => {
    const mockResponse = { 
      data: { 
        status: 'success', 
        message: 'Data deletion request processed successfully' 
      } 
    };
    
    vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

    const result = await gdprService.deleteUserData(mockSessionId, mockReason);

    expect(apiClient.post).toHaveBeenCalledTimes(1);
    expect(apiClient.post).toHaveBeenCalledWith('/gdpr/delete', {
      session_id: mockSessionId,
      reason: mockReason,
    });
    expect(result).toEqual(mockResponse.data);
  });

  it('should call delete endpoint with correct parameters without reason', async () => {
    const mockResponse = { 
      data: { 
        status: 'success', 
        message: 'Data deletion request processed successfully' 
      } 
    };
    
    vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

    const result = await gdprService.deleteUserData(mockSessionId);

    expect(apiClient.post).toHaveBeenCalledTimes(1);
    expect(apiClient.post).toHaveBeenCalledWith('/gdpr/delete', {
      session_id: mockSessionId,
      reason: undefined,
    });
    expect(result).toEqual(mockResponse.data);
  });

  it('should propagate errors from the API client', async () => {
    const mockError = new Error('API Error');
    vi.mocked(apiClient.post).mockRejectedValue(mockError);

    await expect(gdprService.deleteUserData(mockSessionId))
      .rejects
      .toThrow('API Error');
  });
});
