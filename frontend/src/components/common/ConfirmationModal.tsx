import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isLoading?: boolean;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  isLoading = false,
}) => {
  const modalRef = useRef<HTMLDivElement>(null);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen && !isLoading) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      // Focus modal when opened
      modalRef.current?.focus();
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose, isLoading]);

  // Trap focus or simple background click close
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget && !isLoading) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div 
        ref={modalRef}
        className="bg-white rounded-xl shadow-xl max-w-md w-full overflow-hidden animate-in fade-in zoom-in-95 duration-200"
        tabIndex={-1}
      >
        <div className="flex justify-between items-center p-4 border-b border-gray-100">
          <h3 id="modal-title" className="text-lg font-semibold text-gray-900">
            {title}
          </h3>
          <button 
            onClick={onClose}
            disabled={isLoading}
            className="text-gray-400 hover:text-gray-500 hover:bg-gray-100 p-1 rounded-full transition-colors disabled:opacity-50"
            aria-label="Close modal"
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="p-6">
          <p className="text-gray-600">
            {message}
          </p>
        </div>

        <div className="p-4 bg-gray-50 flex justify-end gap-3 rounded-b-xl">
          <button
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 disabled:opacity-50 transition-colors"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 flex items-center gap-2 transition-colors"
          >
            {isLoading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                Processing...
              </>
            ) : (
              confirmText
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
