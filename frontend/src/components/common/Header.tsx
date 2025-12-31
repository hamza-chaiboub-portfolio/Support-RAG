import React from 'react';
import { MessageSquare, LogOut } from 'lucide-react';

interface HeaderProps {
  isAuthenticated?: boolean;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ isAuthenticated, onLogout }) => {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
      <div className="flex items-center space-x-2 text-sky-600">
        <MessageSquare className="w-6 h-6" />
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">SupportRAG</h1>
      </div>
      
      {isAuthenticated && onLogout && (
        <button
          onClick={onLogout}
          className="flex items-center text-sm text-gray-600 hover:text-red-600 transition-colors"
        >
          <LogOut className="w-4 h-4 mr-1" />
          Sign Out
        </button>
      )}
    </header>
  );
};
