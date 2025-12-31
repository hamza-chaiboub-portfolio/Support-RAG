import React, { useRef } from 'react';
import { useForm } from 'react-hook-form';
import { Send, Paperclip } from 'lucide-react';
import { LoadingSpinner } from '../common/LoadingSpinner';

interface InputFieldProps {
  onSendMessage: (message: string) => void;
  onUploadFile: (file: File) => void;
  isLoading: boolean;
}

interface FormInputs {
  message: string;
}

export const InputField: React.FC<InputFieldProps> = ({ onSendMessage, onUploadFile, isLoading }) => {
  const { register, handleSubmit, reset, formState: { isValid } } = useForm<FormInputs>();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const onSubmit = (data: FormInputs) => {
    if (data.message.trim() && !isLoading) {
      onSendMessage(data.message);
      reset();
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onUploadFile(file);
      // Reset input value so same file can be uploaded again
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="border-t border-gray-200 bg-white p-4">
      <div className="relative flex items-center max-w-4xl mx-auto space-x-2">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept=".pdf,.txt,.docx,.doc,.md,.json"
        />
        <button
          type="button"
          onClick={triggerFileUpload}
          disabled={isLoading}
          className="p-2 text-gray-500 hover:text-sky-600 disabled:text-gray-300 transition-colors"
          title="Upload document"
        >
          <Paperclip size={20} />
        </button>
        <div className="relative flex-1">
          <input
            {...register('message', { required: true })}
            type="text"
            placeholder="Type your question..."
            className="input-field pr-12"
            disabled={isLoading}
            autoComplete="off"
          />
          <button
            type="submit"
            disabled={!isValid || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-sky-600 hover:text-sky-700 disabled:text-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? <LoadingSpinner size={20} /> : <Send size={20} />}
          </button>
        </div>
      </div>
    </form>
  );
};
