import React, { useState } from 'react';
import { useSession } from '../../hooks/useSession';
import { gdprService } from '../../services/gdpr.service';
import { ConfirmationModal } from './ConfirmationModal';
import { AlertBox } from './AlertBox';

export const Footer: React.FC = () => {
  const { sessionId } = useSession();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteStatus, setDeleteStatus] = useState<{type: 'success'|'error', message: string} | null>(null);

  const handleDelete = async () => {
    if (!sessionId) return;
    
    setIsDeleting(true);
    try {
      await gdprService.deleteUserData(sessionId);
      setDeleteStatus({
        type: 'success',
        message: 'Your data deletion request has been processed successfully.'
      });
      setShowDeleteModal(false);
    } catch (error) {
      console.error('Failed to delete data:', error);
      setDeleteStatus({
        type: 'error',
        message: 'Failed to request data deletion. Please try again later.'
      });
      setShowDeleteModal(false);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <footer className="bg-gray-50 border-t border-gray-200 px-6 py-4 mt-auto relative">
      <div className="max-w-4xl mx-auto flex flex-col md:flex-row justify-between items-center text-sm text-gray-500 gap-4">
        <p>© {new Date().getFullYear()} SupportRAG. All rights reserved.</p>
        <div className="flex items-center space-x-6">
          <a href="#" className="hover:text-sky-600 transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-sky-600 transition-colors">Terms of Service</a>
          <button 
            onClick={() => setShowDeleteModal(true)}
            className="text-gray-500 hover:text-red-600 transition-colors"
            aria-label="Delete my data"
          >
            Delete my data
          </button>
        </div>
      </div>

      <ConfirmationModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDelete}
        title="Delete Personal Data"
        message="Are you sure you want to delete your personal data? This action cannot be undone and will remove your conversation history."
        confirmText="Delete My Data"
        isLoading={isDeleting}
      />

      {deleteStatus && (
        <div className="fixed bottom-4 right-4 z-50 animate-in slide-in-from-bottom-5 fade-in duration-300 max-w-sm w-full px-4 md:px-0">
          <AlertBox 
            type={deleteStatus.type} 
            message={deleteStatus.message} 
            onClose={() => setDeleteStatus(null)} 
            className="shadow-lg bg-white"
          />
        </div>
      )}
    </footer>
  );
};
