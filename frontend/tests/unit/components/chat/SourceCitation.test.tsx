import { render, screen } from '@testing-library/react';
import { SourceCitation } from '../../../../src/components/chat/SourceCitation';
import type { ChatSource } from '../../../../src/types/chat.types';

describe('SourceCitation', () => {
  it('should return null when no sources are provided', () => {
    const { container } = render(<SourceCitation sources={undefined} />);
    expect(container.firstChild).toBeNull();
  });

  it('should return null when sources array is empty', () => {
    const { container } = render(<SourceCitation sources={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it('should render sources with title and link', () => {
    const sources: ChatSource[] = [
      {
        title: 'Test Document',
        url: 'https://example.com/doc',
        relevance_score: 0.95,
      },
    ];

    render(<SourceCitation sources={sources} />);

    expect(screen.getByText('Test Document')).toBeInTheDocument();
    expect(screen.getByRole('link')).toHaveAttribute('href', 'https://example.com/doc');
  });

  it('should display relevance score as percentage', () => {
    const sources: ChatSource[] = [
      {
        title: 'Document',
        url: 'https://example.com',
        relevance_score: 0.87,
      },
    ];

    render(<SourceCitation sources={sources} />);

    expect(screen.getByText('Relevance: 87%')).toBeInTheDocument();
  });

  it('should display confidence score when provided', () => {
    const sources: ChatSource[] = [
      {
        title: 'Document',
        url: 'https://example.com',
        relevance_score: 0.9,
      },
    ];

    const { container } = render(<SourceCitation sources={sources} confidence_score={0.92} />);

    expect(container.textContent).toContain('Confidence:');
    expect(container.textContent).toContain('92%');
  });

  it('should not display confidence score when not provided', () => {
    const sources: ChatSource[] = [
      {
        title: 'Document',
        url: 'https://example.com',
        relevance_score: 0.9,
      },
    ];

    const { container } = render(<SourceCitation sources={sources} />);

    expect(container.textContent).not.toContain('Confidence:');
  });

  it('should render multiple sources', () => {
    const sources: ChatSource[] = [
      {
        title: 'First Document',
        url: 'https://example.com/doc1',
        relevance_score: 0.95,
      },
      {
        title: 'Second Document',
        url: 'https://example.com/doc2',
        relevance_score: 0.85,
      },
      {
        title: 'Third Document',
        url: 'https://example.com/doc3',
        relevance_score: 0.75,
      },
    ];

    render(<SourceCitation sources={sources} />);

    expect(screen.getByText('First Document')).toBeInTheDocument();
    expect(screen.getByText('Second Document')).toBeInTheDocument();
    expect(screen.getByText('Third Document')).toBeInTheDocument();
  });

  it('should open links in new tab with security attributes', () => {
    const sources: ChatSource[] = [
      {
        title: 'Document',
        url: 'https://example.com',
        relevance_score: 0.9,
      },
    ];

    render(<SourceCitation sources={sources} />);

    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('should display Sources heading', () => {
    const sources: ChatSource[] = [
      {
        title: 'Document',
        url: 'https://example.com',
        relevance_score: 0.9,
      },
    ];

    render(<SourceCitation sources={sources} />);

    expect(screen.getByText('Sources')).toBeInTheDocument();
  });
});
