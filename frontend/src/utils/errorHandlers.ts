import type { ApiError } from '../types/api.types';

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === 'object' && error !== null && 'detail' in error) {
    const apiError = error as ApiError;
    return apiError.detail || 'An unknown error occurred';
  }

  if (typeof error === 'string') {
    return error;
  }

  return 'An unknown error occurred. Please try again.';
}

export function isNetworkError(error: unknown): boolean {
  if (error instanceof Error) {
    return (
      error.message.includes('Network') ||
      error.message.includes('fetch') ||
      error.message.includes('ERR_NETWORK')
    );
  }
  return false;
}

export function isTimeoutError(error: unknown): boolean {
  if (error instanceof Error) {
    return error.message.includes('timeout') || error.message.includes('TIMEOUT');
  }
  return false;
}

export function getRetryableError(error: unknown): boolean {
  return isNetworkError(error) || isTimeoutError(error);
}

export function formatApiError(error: unknown): string {
  if (isNetworkError(error)) {
    return 'Unable to reach the support system. Please check your connection and try again.';
  }

  if (isTimeoutError(error)) {
    return 'Request timed out. Please try again.';
  }

  return getErrorMessage(error);
}
