import { render, screen } from '@testing-library/react';
import { MessageBubble } from '../../../../src/components/chat/MessageBubble';
import type { ChatMessage } from '../../../../src/types/chat.types';

describe('MessageBubble', () => {
  it('should render user message', () => {
    const message: ChatMessage = {
      id: 'msg-1',
      role: 'user',
      content: 'What is your return policy?',
      timestamp: Date.now(),
      status: 'sent',
    };

    const { container } = render(<MessageBubble message={message} />);

    expect(screen.getByText('What is your return policy?')).toBeInTheDocument();
    expect(container.querySelector('.message-user')).toBeInTheDocument();
  });

  it('should render assistant message', () => {
    const message: ChatMessage = {
      id: 'msg-2',
      role: 'assistant',
      content: 'Our return policy allows returns within 30 days.',
      timestamp: Date.now(),
      status: 'sent',
    };

    const { container } = render(<MessageBubble message={message} />);

    expect(screen.getByText('Our return policy allows returns within 30 days.')).toBeInTheDocument();
    expect(container.querySelector('.message-assistant')).toBeInTheDocument();
  });

  it('should display timestamp for user message', () => {
    const now = Date.now();
    const message: ChatMessage = {
      id: 'msg-1',
      role: 'user',
      content: 'Test message',
      timestamp: now,
      status: 'sent',
    };

    const { container } = render(<MessageBubble message={message} />);

    const timeElements = container.querySelectorAll('div.text-xs');
    expect(timeElements.length).toBeGreaterThan(0);
  });

  it('should display timestamp for assistant message', () => {
    const now = Date.now();
    const message: ChatMessage = {
      id: 'msg-1',
      role: 'assistant',
      content: 'Test response',
      timestamp: now,
      status: 'sent',
    };

    const { container } = render(<MessageBubble message={message} />);

    const timeElements = container.querySelectorAll('div.text-xs');
    expect(timeElements.length).toBeGreaterThan(0);
  });

  it('should render assistant message with sources', () => {
    const message: ChatMessage = {
      id: 'msg-2',
      role: 'assistant',
      content: 'Our return policy allows returns within 30 days.',
      timestamp: Date.now(),
      status: 'sent',
      sources: [
        {
          title: 'Return Policy',
          url: 'https://example.com/returns',
          relevance_score: 0.95,
        },
      ],
      confidence_score: 0.92,
    };

    render(<MessageBubble message={message} />);

    expect(screen.getByText('Sources')).toBeInTheDocument();
    expect(screen.getByText('Return Policy')).toBeInTheDocument();
  });

  it('should not render sources for user message', () => {
    const message: ChatMessage = {
      id: 'msg-1',
      role: 'user',
      content: 'What is your return policy?',
      timestamp: Date.now(),
      status: 'sent',
      sources: [
        {
          title: 'Return Policy',
          url: 'https://example.com/returns',
          relevance_score: 0.95,
        },
      ],
    };

    const { container } = render(<MessageBubble message={message} />);

    expect(container.textContent).not.toContain('Sources');
  });

  it('should render multiple sources for assistant message', () => {
    const message: ChatMessage = {
      id: 'msg-2',
      role: 'assistant',
      content: 'Here is information about returns.',
      timestamp: Date.now(),
      status: 'sent',
      sources: [
        {
          title: 'Return Policy Guide',
          url: 'https://example.com/returns',
          relevance_score: 0.98,
        },
        {
          title: 'FAQ',
          url: 'https://example.com/faq',
          relevance_score: 0.87,
        },
        {
          title: 'Support Article',
          url: 'https://example.com/support',
          relevance_score: 0.75,
        },
      ],
      confidence_score: 0.91,
    };

    render(<MessageBubble message={message} />);

    expect(screen.getByText('Return Policy Guide')).toBeInTheDocument();
    expect(screen.getByText('FAQ')).toBeInTheDocument();
    expect(screen.getByText('Support Article')).toBeInTheDocument();
  });

  it('should display confidence score with assistant message sources', () => {
    const message: ChatMessage = {
      id: 'msg-2',
      role: 'assistant',
      content: 'Test response',
      timestamp: Date.now(),
      status: 'sent',
      sources: [
        {
          title: 'Document',
          url: 'https://example.com/doc',
          relevance_score: 0.9,
        },
      ],
      confidence_score: 0.85,
    };

    const { container } = render(<MessageBubble message={message} />);

    expect(container.textContent).toContain('Confidence:');
    expect(container.textContent).toContain('85%');
  });

  it('should not render source section when no sources provided to assistant', () => {
    const message: ChatMessage = {
      id: 'msg-2',
      role: 'assistant',
      content: 'Test response without sources',
      timestamp: Date.now(),
      status: 'sent',
      confidence_score: 0.8,
    };

    const { container } = render(<MessageBubble message={message} />);

    expect(container.textContent).not.toContain('Sources');
  });

  it('should render message with whitespace preserved', () => {
    const message: ChatMessage = {
      id: 'msg-1',
      role: 'user',
      content: 'Line 1\nLine 2\nLine 3',
      timestamp: Date.now(),
      status: 'sent',
    };

    const { container } = render(<MessageBubble message={message} />);

    const contentDiv = container.querySelector('.whitespace-pre-wrap');
    expect(contentDiv).toHaveClass('whitespace-pre-wrap');
    expect(contentDiv?.textContent).toContain('Line 1');
    expect(contentDiv?.textContent).toContain('Line 2');
    expect(contentDiv?.textContent).toContain('Line 3');
  });

  it('should align user messages to the right', () => {
    const message: ChatMessage = {
      id: 'msg-1',
      role: 'user',
      content: 'User message',
      timestamp: Date.now(),
      status: 'sent',
    };

    const { container } = render(<MessageBubble message={message} />);

    const wrapper = container.querySelector('.justify-end');
    expect(wrapper).toBeInTheDocument();
  });

  it('should align assistant messages to the left', () => {
    const message: ChatMessage = {
      id: 'msg-2',
      role: 'assistant',
      content: 'Assistant message',
      timestamp: Date.now(),
      status: 'sent',
    };

    const { container } = render(<MessageBubble message={message} />);

    const wrapper = container.querySelector('.justify-start');
    expect(wrapper).toBeInTheDocument();
  });
});
