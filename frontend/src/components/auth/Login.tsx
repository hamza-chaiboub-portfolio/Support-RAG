import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Lock, User, AlertCircle, Loader2 } from 'lucide-react';
import { authService } from '../../services/authService';
import type { LoginRequest } from '../../types/api.types';

interface LoginProps {
  onLoginSuccess: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const { register, handleSubmit, formState: { errors } } = useForm<LoginRequest>();

  const onSubmit = async (data: LoginRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await authService.login(data);
      onLoginSuccess();
    } catch (err: unknown) {
      console.error('Login failed:', err);
      // Try to extract useful error message
      let message = 'Login failed. Please check your credentials.';
      
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response: { data: { detail: string } } };
        if (axiosError.response?.data?.detail) {
          message = axiosError.response.data.detail;
        }
      }
      
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-6 sm:p-8">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Welcome Back</h2>
          <p className="text-gray-600 mt-2">Please sign in to your account</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-gray-400" />
              </div>
              <input
                id="username"
                {...register('username', { required: 'Username is required' })}
                type="text"
                className={`block w-full pl-10 pr-3 py-2 border ${
                  errors.username ? 'border-red-300' : 'border-gray-300'
                } rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm`}
                placeholder="Enter your username"
              />
            </div>
            {errors.username && (
              <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <input
                id="password"
                {...register('password', { required: 'Password is required' })}
                type="password"
                className={`block w-full pl-10 pr-3 py-2 border ${
                  errors.password ? 'border-red-300' : 'border-gray-300'
                } rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm`}
                placeholder="Enter your password"
              />
            </div>
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {isLoading ? (
              <>
                <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                Signing in...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
