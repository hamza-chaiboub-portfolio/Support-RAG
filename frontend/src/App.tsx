import { useState, useEffect } from 'react';
import { ChatProvider } from './context/ChatProvider';
import { Header } from './components/common/Header';
import { Footer } from './components/common/Footer';
import { ChatInterface } from './components/chat/ChatInterface';
import { ErrorBoundary } from './components/chat/ErrorBoundary';
import { Login } from './components/auth/Login';
import { authService } from './services/authService';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check authentication status only once on mount
    const checkAuth = () => {
      const authStatus = authService.isAuthenticated();
      setIsAuthenticated(authStatus);
      setIsLoading(false);
    };
    
    checkAuth();
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  if (!isAuthenticated) {
    return (
      <div className="flex flex-col h-screen bg-gray-50">
        <Header />
        <main className="flex-1 flex items-center justify-center p-4">
          <Login onLoginSuccess={handleLoginSuccess} />
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <ChatProvider>
      <div className="flex flex-col h-screen bg-gray-50">
        <Header isAuthenticated={true} onLogout={handleLogout} />
        
        <main className="flex-1 max-w-4xl w-full mx-auto p-4 md:p-6 overflow-hidden flex flex-col">
          <ErrorBoundary>
            <ChatInterface />
          </ErrorBoundary>
        </main>
        
        <Footer />
      </div>
    </ChatProvider>
  );
}

export default App;
