import React from 'react';
import { AlertCircle, X, CheckCircle, Info } from 'lucide-react';

export type AlertType = 'error' | 'success' | 'info' | 'warning';

interface AlertBoxProps {
  type?: AlertType;
  message: string;
  onClose?: () => void;
  className?: string;
}

const styles = {
  error: 'bg-red-50 text-red-700 border-red-200',
  success: 'bg-green-50 text-green-700 border-green-200',
  info: 'bg-blue-50 text-blue-700 border-blue-200',
  warning: 'bg-yellow-50 text-yellow-700 border-yellow-200',
};

const icons = {
  error: AlertCircle,
  success: CheckCircle,
  info: Info,
  warning: AlertCircle,
};

export const AlertBox: React.FC<AlertBoxProps> = ({ 
  type = 'error', 
  message, 
  onClose,
  className = '' 
}) => {
  const Icon = icons[type];

  return (
    <div className={`flex items-center p-4 mb-4 border rounded-lg ${styles[type]} ${className}`}>
      <Icon className="w-5 h-5 flex-shrink-0 mr-3" />
      <div className="flex-1 text-sm font-medium">{message}</div>
      {onClose && (
        <button 
          onClick={onClose}
          className="ml-auto p-1.5 rounded-lg hover:bg-black/5 transition-colors"
          aria-label="Close"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
};
