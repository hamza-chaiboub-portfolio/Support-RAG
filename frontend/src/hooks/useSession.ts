import { useState, useCallback } from 'react';
import { getSessionId, regenerateSessionId, clearSessionId } from '../utils/sessionUtils';

export interface UseSessionReturn {
  sessionId: string;
  refreshSession: () => void;
  clearSession: () => void;
}

export function useSession(): UseSessionReturn {
  // Initialize with current session ID (generates one if missing)
  const [sessionId, setSessionId] = useState<string>(() => getSessionId());

  const refreshSession = useCallback(() => {
    const newId = regenerateSessionId();
    setSessionId(newId);
  }, []);

  const clearSession = useCallback(() => {
    clearSessionId();
    setSessionId('');
  }, []);

  return {
    sessionId,
    refreshSession,
    clearSession
  };
}
