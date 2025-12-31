import { render, screen, fireEvent } from '@testing-library/react';
import { ConfirmationModal } from '../../../../src/components/common/ConfirmationModal';

describe('ConfirmationModal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onConfirm: vi.fn(),
    title: 'Confirm Action',
    message: 'Are you sure?',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should not render when isOpen is false', () => {
    render(<ConfirmationModal {...defaultProps} isOpen={false} />);
    
    expect(screen.queryByText('Confirm Action')).not.toBeInTheDocument();
    expect(screen.queryByText('Are you sure?')).not.toBeInTheDocument();
  });

  it('should render correct content when isOpen is true', () => {
    render(<ConfirmationModal {...defaultProps} />);
    
    expect(screen.getByText('Confirm Action')).toBeInTheDocument();
    expect(screen.getByText('Are you sure?')).toBeInTheDocument();
    expect(screen.getByText('Confirm')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', () => {
    render(<ConfirmationModal {...defaultProps} />);
    
    const closeButton = screen.getByLabelText('Close modal');
    fireEvent.click(closeButton);
    
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('should call onClose when cancel button is clicked', () => {
    render(<ConfirmationModal {...defaultProps} />);
    
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);
    
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('should call onConfirm when confirm button is clicked', () => {
    render(<ConfirmationModal {...defaultProps} />);
    
    const confirmButton = screen.getByText('Confirm');
    fireEvent.click(confirmButton);
    
    expect(defaultProps.onConfirm).toHaveBeenCalledTimes(1);
  });

  it('should show loading state and disable buttons when isLoading is true', () => {
    render(<ConfirmationModal {...defaultProps} isLoading={true} />);
    
    expect(screen.getByText('Processing...')).toBeInTheDocument();
    
    const cancelButton = screen.getByText('Cancel');
    const closeButton = screen.getByLabelText('Close modal');
    // The confirm button text changes to "Processing..." so we find it by that
    const confirmButton = screen.getByText('Processing...').closest('button');

    expect(cancelButton).toBeDisabled();
    expect(closeButton).toBeDisabled();
    expect(confirmButton).toBeDisabled();
  });

  it('should close on Escape key press', () => {
    render(<ConfirmationModal {...defaultProps} />);
    
    fireEvent.keyDown(document, { key: 'Escape' });
    
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('should close on backdrop click', () => {
    render(<ConfirmationModal {...defaultProps} />);
    
    // The backdrop is the outer div with role="dialog"
    const backdrop = screen.getByRole('dialog');
    fireEvent.click(backdrop);
    
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('should not close on backdrop click if isLoading is true', () => {
    render(<ConfirmationModal {...defaultProps} isLoading={true} />);
    
    const backdrop = screen.getByRole('dialog');
    fireEvent.click(backdrop);
    
    expect(defaultProps.onClose).not.toHaveBeenCalled();
  });

  it('should not close on Escape key if isLoading is true', () => {
    render(<ConfirmationModal {...defaultProps} isLoading={true} />);
    
    fireEvent.keyDown(document, { key: 'Escape' });
    
    expect(defaultProps.onClose).not.toHaveBeenCalled();
  });
});
