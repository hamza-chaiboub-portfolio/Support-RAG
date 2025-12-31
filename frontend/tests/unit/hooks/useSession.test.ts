import { renderHook, act } from '@testing-library/react';
import { useSession } from '../../../src/hooks/useSession';
import * as sessionUtils from '../../../src/utils/sessionUtils';

// Mock sessionUtils
vi.mock('../../../src/utils/sessionUtils', () => ({
  getSessionId: vi.fn(),
  regenerateSessionId: vi.fn(),
  clearSessionId: vi.fn(),
}));

describe('useSession', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with session ID', () => {
    vi.mocked(sessionUtils.getSessionId).mockReturnValue('initial-id');
    
    const { result } = renderHook(() => useSession());
    
    expect(result.current.sessionId).toBe('initial-id');
    expect(sessionUtils.getSessionId).toHaveBeenCalledTimes(1);
  });

  it('should refresh session', () => {
    vi.mocked(sessionUtils.getSessionId).mockReturnValue('initial-id');
    vi.mocked(sessionUtils.regenerateSessionId).mockReturnValue('new-id');
    
    const { result } = renderHook(() => useSession());
    
    act(() => {
      result.current.refreshSession();
    });
    
    expect(sessionUtils.regenerateSessionId).toHaveBeenCalledTimes(1);
    expect(result.current.sessionId).toBe('new-id');
  });

  it('should clear session', () => {
    vi.mocked(sessionUtils.getSessionId).mockReturnValue('initial-id');
    
    const { result } = renderHook(() => useSession());
    
    act(() => {
      result.current.clearSession();
    });
    
    expect(sessionUtils.clearSessionId).toHaveBeenCalledTimes(1);
    expect(result.current.sessionId).toBe('');
  });
});
