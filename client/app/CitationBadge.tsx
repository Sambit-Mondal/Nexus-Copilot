/**
 * Citation Badge Component
 * Displays source document information for AI responses
 */

import React from 'react';
import { Citation } from './types';

interface CitationBadgeProps {
  citations: Citation[];
  inline?: boolean;
}

export const CitationBadge: React.FC<CitationBadgeProps> = ({
  citations,
  inline = true,
}) => {
  if (citations.length === 0) return null;

  if (inline) {
    return (
      <div className="flex flex-wrap gap-2 mt-3">
        {citations.map((citation, idx) => (
          <div
            key={idx}
            className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 border border-blue-200 rounded-full text-xs text-blue-700 hover:bg-blue-100 transition cursor-default"
            title={`${citation.filename}${citation.page_number ? ` - Page ${citation.page_number}` : ''} (${Math.round(citation.confidence * 100)}% confidence)`}
          >
            <span className="text-sm">📄</span>
            <span className="font-medium">{citation.filename}</span>
            {citation.page_number && (
              <span className="text-blue-600">p.{citation.page_number}</span>
            )}
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="mt-4 pt-4 border-t border-gray-200">
      <p className="text-xs font-semibold text-gray-600 mb-2">Sources:</p>
      <div className="space-y-2">
        {citations.map((citation, idx) => (
          <div
            key={idx}
            className="flex items-start gap-2 p-2 bg-gray-50 rounded border border-gray-200 text-xs text-gray-700"
          >
            <span className="text-base flex-shrink-0">📄</span>
            <div className="flex-1">
              <p className="font-medium">{citation.filename}</p>
              <div className="flex items-center gap-2 text-gray-500 mt-1">
                {citation.page_number && <span>Page {citation.page_number}</span>}
                <span>
                  {Math.round(citation.confidence * 100)}% confidence
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CitationBadge;
