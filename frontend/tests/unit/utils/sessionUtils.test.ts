import { getSessionId, clearSessionId, regenerateSessionId, generateUUID } from '../../../src/utils/sessionUtils';

describe('sessionUtils', () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.restoreAllMocks();
  });

  describe('generateUUID', () => {
    it('should generate a valid UUID format', () => {
      const uuid = generateUUID();
      expect(uuid).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });

    it('should generate unique UUIDs', () => {
      const uuid1 = generateUUID();
      const uuid2 = generateUUID();
      expect(uuid1).not.toBe(uuid2);
    });
  });

  describe('getSessionId', () => {
    it('should return existing session ID from storage', () => {
      const existingId = 'existing-id';
      sessionStorage.setItem('supportrag_session_id', existingId);
      expect(getSessionId()).toBe(existingId);
    });

    it('should generate and store new session ID if none exists', () => {
      const id = getSessionId();
      expect(id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
      expect(sessionStorage.getItem('supportrag_session_id')).toBe(id);
    });

    it('should handle sessionStorage errors gracefully', () => {
      // Mock sessionStorage.getItem to throw error
      vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
        throw new Error('Access denied');
      });

      const id = getSessionId();
      expect(id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });
  });

  describe('clearSessionId', () => {
    it('should remove session ID from storage', () => {
      sessionStorage.setItem('supportrag_session_id', 'to-be-removed');
      clearSessionId();
      expect(sessionStorage.getItem('supportrag_session_id')).toBeNull();
    });

    it('should handle sessionStorage errors gracefully', () => {
       vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => {
        throw new Error('Access denied');
      });
      
      expect(() => clearSessionId()).not.toThrow();
    });
  });

  describe('regenerateSessionId', () => {
    it('should generate a new ID different from the previous one', () => {
      const oldId = getSessionId();
      const newId = regenerateSessionId();
      
      expect(newId).not.toBe(oldId);
      expect(newId).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
      expect(sessionStorage.getItem('supportrag_session_id')).toBe(newId);
    });
  });
});
