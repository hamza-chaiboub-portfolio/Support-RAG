import apiClient from './api';
import type { LoginRequest, LoginResponse } from '../types/api.types';
import { setAuthToken, setUserId, clearAuth, setCsrfToken } from '../utils/tokenUtils';

interface CsrfTokenResponse {
  csrf_token: string;
}

const fetchCsrfToken = async (): Promise<string | null> => {
  try {
    const response = await apiClient.get<CsrfTokenResponse>('/auth/csrf');
    const token = response.data.csrf_token;
    if (token) {
      setCsrfToken(token);
    }
    return token || null;
  } catch (error) {
    console.warn('Failed to fetch CSRF token:', error);
    return null;
  }
};

export const authService = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    await fetchCsrfToken();
    
    const response = await apiClient.post<LoginResponse>('/auth/login', credentials);
    const data = response.data;
    
    setAuthToken(data.access_token);
    setUserId(data.user_id);
    
    return data;
  },

  logout(): void {
    clearAuth();
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('supportrag_auth_token');
  }
};
