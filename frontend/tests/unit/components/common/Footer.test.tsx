import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Footer } from '../../../../src/components/common/Footer';
import { gdprService } from '../../../../src/services/gdpr.service';
import { useSession } from '../../../../src/hooks/useSession';

// Mock dependencies
vi.mock('../../../../src/services/gdpr.service', () => ({
  gdprService: {
    deleteUserData: vi.fn(),
  },
}));

vi.mock('../../../../src/hooks/useSession', () => ({
  useSession: vi.fn(),
}));

describe('Footer', () => {
  const mockSessionId = 'test-session-id';
  const mockDeleteUserData = vi.mocked(gdprService.deleteUserData);
  const mockUseSession = vi.mocked(useSession);

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseSession.mockReturnValue({
      sessionId: mockSessionId,
      refreshSession: vi.fn(),
      clearSession: vi.fn(),
    });
  });

  it('should render footer links and copyright', () => {
    render(<Footer />);
    
    expect(screen.getByText(/SupportRAG. All rights reserved./)).toBeInTheDocument();
    expect(screen.getByText('Privacy Policy')).toBeInTheDocument();
    expect(screen.getByText('Terms of Service')).toBeInTheDocument();
    expect(screen.getByText('Delete my data')).toBeInTheDocument();
  });

  it('should open confirmation modal when "Delete my data" is clicked', () => {
    render(<Footer />);
    
    // Modal should be closed initially
    expect(screen.queryByText('Delete Personal Data')).not.toBeInTheDocument();
    
    // Click delete button
    fireEvent.click(screen.getByText('Delete my data'));
    
    // Modal should be open
    expect(screen.getByText('Delete Personal Data')).toBeInTheDocument();
    expect(screen.getByText('Are you sure you want to delete your personal data? This action cannot be undone and will remove your conversation history.')).toBeInTheDocument();
  });

  it('should handle successful data deletion', async () => {
    mockDeleteUserData.mockResolvedValue({ status: 'success', message: 'Deleted' });
    
    render(<Footer />);
    
    // Open modal
    fireEvent.click(screen.getByText('Delete my data'));
    
    // Click confirm in modal
    fireEvent.click(screen.getByText('Delete My Data'));
    
    // Verify service call
    expect(mockDeleteUserData).toHaveBeenCalledWith(mockSessionId);
    
    // Verify success message
    await waitFor(() => {
      expect(screen.getByText('Your data deletion request has been processed successfully.')).toBeInTheDocument();
    });
    
    // Verify modal is closed
    await waitFor(() => {
      expect(screen.queryByText('Delete Personal Data')).not.toBeInTheDocument();
    });
  });

  it('should handle failed data deletion', async () => {
    mockDeleteUserData.mockRejectedValue(new Error('API Error'));
    
    render(<Footer />);
    
    // Open modal
    fireEvent.click(screen.getByText('Delete my data'));
    
    // Click confirm in modal
    fireEvent.click(screen.getByText('Delete My Data'));
    
    // Verify service call
    expect(mockDeleteUserData).toHaveBeenCalledWith(mockSessionId);
    
    // Verify error message
    await waitFor(() => {
      expect(screen.getByText('Failed to request data deletion. Please try again later.')).toBeInTheDocument();
    });
    
    // Verify modal is closed
    await waitFor(() => {
      expect(screen.queryByText('Delete Personal Data')).not.toBeInTheDocument();
    });
  });

  it('should not attempt deletion if session ID is missing', async () => {
    mockUseSession.mockReturnValue({
      sessionId: '',
      refreshSession: vi.fn(),
      clearSession: vi.fn(),
    });
    
    render(<Footer />);
    
    // Open modal
    fireEvent.click(screen.getByText('Delete my data'));
    
    // Click confirm in modal
    fireEvent.click(screen.getByText('Delete My Data'));
    
    // Verify service NOT called
    expect(mockDeleteUserData).not.toHaveBeenCalled();
  });

  it('should cancel deletion when Cancel is clicked', () => {
    render(<Footer />);
    
    // Open modal
    fireEvent.click(screen.getByText('Delete my data'));
    
    // Click cancel in modal
    fireEvent.click(screen.getByText('Cancel'));
    
    // Verify service NOT called
    expect(mockDeleteUserData).not.toHaveBeenCalled();
    
    // Verify modal is closed
    expect(screen.queryByText('Delete Personal Data')).not.toBeInTheDocument();
  });
});
