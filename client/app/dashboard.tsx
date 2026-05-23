'use client';

import React, { useState, useCallback, useEffect } from 'react';
import ChatInterface from './ChatInterface';
import DocumentUpload from './DocumentUpload';
import ErrorToast from './ErrorToast';
import { UploadProgress } from './types';
import { generateSessionId } from './api';

export default function Dashboard() {
  const [sessionId, setSessionId] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [apiUrl] = useState(
    process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  );

  // Initialize session on mount
  useEffect(() => {
    setSessionId(generateSessionId());
  }, []);

  const handleUploadStart = useCallback((filename: string) => {
    console.log(`Upload started: ${filename}`);
  }, []);

  const handleUploadProgress = useCallback((progress: UploadProgress) => {
    console.log(`Upload progress: ${progress.filename} - ${progress.progress}%`);
  }, []);

  const handleUploadComplete = useCallback((documentId: string) => {
    setSuccessMessage('📄 Document ready for analysis');
    setTimeout(() => setSuccessMessage(null), 4000);
    console.log(`Upload completed: ${documentId}`);
  }, []);

  const handleError = useCallback((errorMessage: string) => {
    setError(errorMessage);
    console.error('Error:', errorMessage);
  }, []);

  const dismissError = useCallback(() => {
    setError(null);
  }, []);

  const dismissSuccess = useCallback(() => {
    setSuccessMessage(null);
  }, []);

  return (
    <div className="flex h-screen bg-[#0a0a0a]">
      {/* Left Side: Chat Interface */}
      <div className="flex-1 flex flex-col border-r border-[rgba(255,255,255,0.08)] overflow-hidden">
        <div className="flex-1 overflow-hidden">
          {sessionId && (
            <ChatInterface sessionId={sessionId} onError={handleError} />
          )}
        </div>
      </div>

      {/* Right Side: Document Upload */}
      <div className="w-80 flex flex-col border-l border-[rgba(255,255,255,0.08)] bg-[#121212] overflow-hidden">
        {/* Upload Panel */}
        <div className="flex-1 overflow-hidden flex flex-col">
          {sessionId && (
            <DocumentUpload
              onUploadStart={handleUploadStart}
              onUploadProgress={handleUploadProgress}
              onUploadComplete={handleUploadComplete}
              onError={handleError}
            />
          )}
        </div>
      </div>

      {/* Error Toast */}
      {error && (
        <div className="fixed bottom-6 left-6 right-auto max-w-sm z-50">
          <ErrorToast message={error} onDismiss={dismissError} />
        </div>
      )}

      {/* Success Toast */}
      {successMessage && (
        <div className="fixed bottom-6 left-6 right-auto max-w-sm z-50">
          <div className="p-4 bg-[#1a1a1a] border border-[rgba(16,185,129,0.3)] rounded-xl text-emerald-400 flex items-start gap-3 backdrop-blur-sm shadow-lg animate-slide-in-up">
            <span className="text-xl flex-shrink-0">✅</span>
            <div className="flex-1">
              <p className="font-medium text-sm">{successMessage}</p>
            </div>
            <button
              onClick={dismissSuccess}
              className="text-emerald-400/60 hover:text-emerald-400 text-xl transition-colors"
            >
              ×
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
