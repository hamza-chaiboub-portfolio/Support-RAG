import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../../src/App';
import { authService } from '../../src/services/authService';
import { act } from 'react';

// Mock the auth service
vi.mock('../../src/services/authService', () => ({
  authService: {
    login: vi.fn(),
    logout: vi.fn(),
    isAuthenticated: vi.fn(),
  },
}));

// Mock the chat service components to avoid complex setup
vi.mock('../../src/components/chat/ChatInterface', () => ({
  ChatInterface: () => <div data-testid="chat-interface">Chat Interface</div>,
}));

describe('Authentication Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default to not authenticated
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);
  });

  it('should show login screen when not authenticated', async () => {
    await act(async () => {
      render(<App />);
    });

    expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.queryByTestId('chat-interface')).not.toBeInTheDocument();
  });

  it('should show chat interface when already authenticated', async () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(true);

    await act(async () => {
      render(<App />);
    });

    expect(screen.getByTestId('chat-interface')).toBeInTheDocument();
    expect(screen.queryByText('Welcome Back')).not.toBeInTheDocument();
  });

  it('should transition to chat interface after successful login', async () => {
    // Start unauthenticated
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);
    vi.mocked(authService.login).mockResolvedValue({
      access_token: 'fake-token',
      token_type: 'bearer',
      user_id: 1,
    });

    await act(async () => {
      render(<App />);
    });

    // Fill in login form
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } });

    // Submit
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await act(async () => {
      fireEvent.click(submitButton);
    });

    // Should call login service
    expect(authService.login).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123',
    });

    // Should show chat interface
    await waitFor(() => {
      expect(screen.getByTestId('chat-interface')).toBeInTheDocument();
    });
  });

  it('should handle login error', async () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);
    const error = new Error('Invalid credentials');
    // @ts-expect-error Mocking complex error object
    error.response = { data: { detail: 'Invalid credentials' } };
    vi.mocked(authService.login).mockRejectedValue(error);

    await act(async () => {
      render(<App />);
    });

    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'wrongpass' } });

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    });

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
    
    expect(screen.queryByTestId('chat-interface')).not.toBeInTheDocument();
  });

  it('should logout and return to login screen', async () => {
    // Start authenticated
    vi.mocked(authService.isAuthenticated).mockReturnValue(true);

    await act(async () => {
      render(<App />);
    });

    expect(screen.getByTestId('chat-interface')).toBeInTheDocument();

    // Find logout button in Header (we need to make sure Header renders logout button)
    // The Header component text is "Sign Out"
    const logoutButton = screen.getByText('Sign Out');
    
    await act(async () => {
      fireEvent.click(logoutButton);
    });

    expect(authService.logout).toHaveBeenCalled();
    
    // Should return to login
    await waitFor(() => {
      expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    });
  });
});
