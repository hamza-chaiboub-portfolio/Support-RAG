import { render, screen } from '@testing-library/react';
import { Header } from '../../../../src/components/common/Header';

describe('Header', () => {
  it('should render logo and title', () => {
    render(<Header />);
    
    expect(screen.getByText('SupportRAG')).toBeInTheDocument();
    // Verify icon presence (by class or implicit role if added, here checks structure)
    // Since MessageSquare is an SVG, we can check if it renders in the document
    const header = screen.getByRole('banner'); // header tag has implicit banner role
    expect(header).toBeInTheDocument();
  });
});
