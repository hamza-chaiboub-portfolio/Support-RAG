const SESSION_ID_KEY = 'supportrag_session_id';

export function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export function getSessionId(): string {
  try {
    const existing = sessionStorage.getItem(SESSION_ID_KEY);
    if (existing) {
      return existing;
    }

    const newId = generateUUID();
    sessionStorage.setItem(SESSION_ID_KEY, newId);
    return newId;
  } catch {
    return generateUUID();
  }
}

export function clearSessionId(): void {
  try {
    sessionStorage.removeItem(SESSION_ID_KEY);
  } catch {
    // Fallback if sessionStorage unavailable
  }
}

export function regenerateSessionId(): string {
  clearSessionId();
  return getSessionId();
}
