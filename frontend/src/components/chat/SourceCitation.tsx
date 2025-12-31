import React from 'react';
import { ExternalLink, BookOpen } from 'lucide-react';
import type { ChatSource } from '../../types/chat.types';

interface SourceCitationProps {
  sources?: ChatSource[];
  confidence_score?: number;
}

export const SourceCitation: React.FC<SourceCitationProps> = ({ 
  sources, 
  confidence_score 
}) => {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 pt-4 border-t border-gray-200">
      {confidence_score !== undefined && (
        <div className="mb-3 text-xs text-gray-600">
          <span className="font-medium">Confidence: </span>
          <span className="text-gray-700">
            {Math.round(confidence_score * 100)}%
          </span>
        </div>
      )}
      
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs font-medium text-gray-700 mb-2">
          <BookOpen size={14} />
          <span>Sources</span>
        </div>
        
        {sources.map((source, index) => (
          <a
            key={index}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-start gap-2 p-2 rounded-lg hover:bg-gray-100 transition-colors group text-xs"
          >
            <ExternalLink 
              size={12} 
              className="flex-shrink-0 mt-0.5 text-gray-400 group-hover:text-sky-600 transition-colors"
            />
            <div className="flex-1 min-w-0">
              <div className="font-medium text-gray-900 group-hover:text-sky-600 truncate">
                {source.title}
              </div>
              <div className="text-gray-500 text-xs mt-1">
                Relevance: {Math.round(source.relevance_score * 100)}%
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
};
