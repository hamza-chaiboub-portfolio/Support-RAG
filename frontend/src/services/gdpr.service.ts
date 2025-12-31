import apiClient from './api';
import type { GdprDeleteRequest, GdprDeleteResponse } from '../types/api.types';

export const gdprService = {
  /**
   * Request data deletion for the current session/user
   * Endpoints: POST /api/v1/gdpr/delete
   */
  async deleteUserData(sessionId: string, reason?: string): Promise<GdprDeleteResponse> {
    const payload: GdprDeleteRequest = {
      session_id: sessionId,
      reason,
    };
    
    const response = await apiClient.post<GdprDeleteResponse>('/gdpr/delete', payload);
    return response.data;
  }
};
