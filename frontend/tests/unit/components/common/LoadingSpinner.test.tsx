import { render } from '@testing-library/react';
import { LoadingSpinner } from '../../../../src/components/common/LoadingSpinner';

describe('LoadingSpinner', () => {
  it('should render with default props', () => {
    const { container } = render(<LoadingSpinner />);
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('animate-spin');
    expect(svg).toHaveClass('text-sky-600');
    expect(svg).toHaveAttribute('width', '24');
    expect(svg).toHaveAttribute('height', '24');
  });

  it('should render with custom size and className', () => {
    const { container } = render(<LoadingSpinner size={48} className="text-red-500" />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('text-red-500');
    expect(svg).toHaveAttribute('width', '48');
    expect(svg).toHaveAttribute('height', '48');
  });
});
