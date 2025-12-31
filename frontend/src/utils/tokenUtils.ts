const TOKEN_KEY = 'supportrag_auth_token';
const USER_ID_KEY = 'supportrag_user_id';

export const getAuthToken = (): string | null => {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
};

export const setAuthToken = (token: string): void => {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // Fallback if localStorage unavailable
  }
};

export const removeAuthToken = (): void => {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    // Fallback if localStorage unavailable
  }
};

export const getUserId = (): number | null => {
  try {
    const id = localStorage.getItem(USER_ID_KEY);
    return id ? parseInt(id, 10) : null;
  } catch {
    return null;
  }
};

export const setUserId = (id: number): void => {
  try {
    localStorage.setItem(USER_ID_KEY, id.toString());
  } catch {
    // Fallback
  }
};

export const removeUserId = (): void => {
  try {
    localStorage.removeItem(USER_ID_KEY);
  } catch {
    // Fallback
  }
};

export const clearAuth = (): void => {
  removeAuthToken();
  removeUserId();
};

export const getCsrfToken = (): string | null => {
  try {
    return sessionStorage.getItem('supportrag_csrf_token');
  } catch {
    return null;
  }
};

export const setCsrfToken = (token: string): void => {
  try {
    sessionStorage.setItem('supportrag_csrf_token', token);
  } catch {
    // No-op if unavailable
  }
};

export const removeCsrfToken = (): void => {
  try {
    sessionStorage.removeItem('supportrag_csrf_token');
  } catch {
    // No-op if unavailable
  }
};
