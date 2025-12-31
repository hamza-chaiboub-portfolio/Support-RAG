import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { getSessionId } from '../utils/sessionUtils';
import { getAuthToken, getCsrfToken } from '../utils/tokenUtils';
import { formatApiError, getRetryableError } from '../utils/errorHandlers';
import type { ApiError } from '../types/api.types';

interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retryCount?: number;
}

const MAX_RETRIES = 2;
const RETRY_DELAY = 1000;

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const sessionId = getSessionId();
    if (sessionId) {
      config.headers['X-Session-ID'] = sessionId;
    }
    
    const token = getAuthToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as CustomAxiosRequestConfig;

    if (!originalRequest) {
      return Promise.reject(error);
    }

    originalRequest._retryCount = originalRequest._retryCount || 0;

    if (
      getRetryableError(error) &&
      originalRequest._retryCount < MAX_RETRIES
    ) {
      originalRequest._retryCount += 1;
      
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
      
      return apiClient(originalRequest);
    }

    if (!error.response || error.response.status >= 500) {
      console.error('API Error:', formatApiError(error));
    }

    return Promise.reject(error);
  }
);

export default apiClient;
