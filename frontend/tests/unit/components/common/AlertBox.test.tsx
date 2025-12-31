import { render, screen, fireEvent } from '@testing-library/react';
import { AlertBox } from '../../../../src/components/common/AlertBox';

describe('AlertBox', () => {
  it('should render message', () => {
    render(<AlertBox message="Something happened" />);
    expect(screen.getByText('Something happened')).toBeInTheDocument();
  });

  it('should apply styles based on type', () => {
    const { container } = render(<AlertBox message="Error" type="error" />);
    // Check if the first div has the error class
    expect(container.firstChild).toHaveClass('bg-red-50');
    expect(container.firstChild).toHaveClass('text-red-700');
  });

  it('should render correct icon for success', () => {
    const { container } = render(<AlertBox message="Success" type="success" />);
    // Check if svg exists inside
    expect(container.querySelector('svg')).toBeInTheDocument();
    expect(container.firstChild).toHaveClass('bg-green-50');
  });

  it('should render close button if onClose provided', () => {
    const handleClose = vi.fn();
    render(<AlertBox message="Closable" onClose={handleClose} />);
    
    const button = screen.getByLabelText('Close');
    expect(button).toBeInTheDocument();
    
    fireEvent.click(button);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('should not render close button if onClose not provided', () => {
    render(<AlertBox message="Not Closable" />);
    expect(screen.queryByLabelText('Close')).not.toBeInTheDocument();
  });
});
