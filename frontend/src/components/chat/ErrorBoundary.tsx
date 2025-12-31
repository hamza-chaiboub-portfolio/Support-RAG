import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center h-full min-h-[400px] p-6 text-center bg-gray-50 rounded-lg border border-gray-200">
          <div className="bg-red-100 p-4 rounded-full mb-4">
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Something went wrong</h2>
          <p className="text-gray-600 mb-6 max-w-md">
            We encountered an unexpected error. Please try refreshing the page.
          </p>
          {this.state.error && import.meta.env.DEV && (
            <pre className="text-xs text-left bg-gray-100 p-4 rounded mb-6 w-full overflow-auto max-h-40">
              {this.state.error.toString()}
            </pre>
          )}
          <button
            onClick={this.handleReset}
            className="flex items-center px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
