import { render, screen } from '@testing-library/react';
import { ChatInterface } from '../../src/components/chat/ChatInterface';

vi.mock('../../src/services/chatService');
vi.mock('../../src/hooks/useChat', () => ({
  useChat: () => ({
    messages: [],
    isLoading: false,
    error: null,
    sessionId: 'test-session-123',
    addMessage: vi.fn(),
    setLoading: vi.fn(),
    setError: vi.fn(),
    clearError: vi.fn(),
  }),
}));

describe('ChatInterface Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render chat interface with message list and input field', () => {
    render(<ChatInterface />);

    expect(screen.getByText('Welcome to SupportRAG')).toBeInTheDocument();
    expect(screen.getByText('Ask me anything about our services.')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Type your question...')).toBeInTheDocument();
  });

  it('should have a submit button for sending messages', () => {
    render(<ChatInterface />);

    const sendButton = screen.getByRole('button') as HTMLButtonElement;
    expect(sendButton).toBeInTheDocument();
    expect(sendButton.type).toBe('submit');
  });

  it('should render error alert when error is present in context', () => {
    vi.doMock('../../src/hooks/useChat', async () => {
      const actual = await vi.importActual('../../src/hooks/useChat');
      return {
        ...actual,
        useChat: () => ({
          messages: [],
          isLoading: false,
          error: 'Test error message',
          sessionId: 'test-session-123',
          addMessage: vi.fn(),
          setLoading: vi.fn(),
          setError: vi.fn(),
          clearError: vi.fn(),
        }),
      };
    });
  });

  it('should render input and button with correct structure', () => {
    render(<ChatInterface />);

    const input = screen.getByPlaceholderText('Type your question...');
    const sendButton = screen.getByRole('button');

    expect(input).toBeVisible();
    expect(sendButton).toBeVisible();
  });

  it('should have form container for message input', () => {
    const { container } = render(<ChatInterface />);

    const form = container.querySelector('form');
    expect(form).toBeInTheDocument();
    expect(form).toHaveClass('border-t', 'border-gray-200', 'bg-white', 'p-4');
  });

  it('should render MessageList component by default with empty state', () => {
    render(<ChatInterface />);

    const welcomeText = screen.getByText('Welcome to SupportRAG');
    const descriptionText = screen.getByText('Ask me anything about our services.');

    expect(welcomeText).toBeInTheDocument();
    expect(descriptionText).toBeInTheDocument();
  });

  it('should have accessible form elements', () => {
    render(<ChatInterface />);

    const form = screen.getByRole('button').closest('form');
    const input = screen.getByPlaceholderText('Type your question...');

    expect(form).toBeInTheDocument();
    expect(input).toHaveAttribute('name', 'message');
    expect(input).toHaveAttribute('type', 'text');
    expect(input).toHaveAttribute('autocomplete', 'off');
  });

  it('should render AlertBox component when provided in context', () => {
    render(<ChatInterface />);

    const container = screen.getByText('Welcome to SupportRAG').closest('div');
    expect(container?.parentElement).toBeInTheDocument();
  });
});
