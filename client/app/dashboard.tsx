'use client';

import React, { useState, useCallback, useEffect } from 'react';
import ChatInterface from './ChatInterface';
import DocumentUpload from './DocumentUpload';
import HealthCheck from './HealthCheck';
import ErrorToast from './ErrorToast';
import { UploadProgress } from './types';
import { generateSessionId } from './api';

export default function Dashboard() {
  const [sessionId, setSessionId] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [recentUploads, setRecentUploads] = useState<Set<string>>(new Set());
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
    if (progress.status === 'completed') {
      setRecentUploads((prev) => new Set(prev).add(progress.documentId));
    }
    console.log(`Upload progress: ${progress.filename} - ${progress.progress}%`);
  }, []);

  const handleUploadComplete = useCallback((documentId: string) => {
    console.log(`Upload completed: ${documentId}`);
  }, []);

  const handleError = useCallback((errorMessage: string) => {
    setError(errorMessage);
    console.error('Error:', errorMessage);
  }, []);

  const dismissError = useCallback(() => {
    setError(null);
  }, []);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Side: Chat Interface */}
      <div className="flex-1 flex flex-col border-r border-gray-200 overflow-hidden">
        <div className="flex-1 overflow-hidden">
          {sessionId && (
            <ChatInterface sessionId={sessionId} onError={handleError} />
          )}
        </div>
      </div>

      {/* Right Side: Document Upload + Status */}
      <div className="w-80 flex flex-col border-l border-gray-200 bg-white overflow-hidden">
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

        {/* Status Panel */}
        <div className="border-t border-gray-200 p-6 bg-gray-50 space-y-4">
          <HealthCheck apiUrl={apiUrl} />

          {/* Session Info */}
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-xs font-semibold text-blue-700 mb-2">
              Session Info
            </p>
            <p className="text-xs text-blue-600 break-all font-mono">
              {sessionId.substring(0, 20)}...
            </p>
          </div>

          {/* Quick Stats */}
          {recentUploads.size > 0 && (
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <p className="text-xs font-semibold text-green-700">
                ✅ {recentUploads.size} Document{recentUploads.size !== 1 ? 's' : ''}
              </p>
              <p className="text-xs text-green-600 mt-1">Ready for analysis</p>
            </div>
          )}
        </div>
      </div>

      {/* Error Toast */}
      {error && (
        <div className="fixed bottom-6 left-6 right-auto max-w-sm z-50">
          <ErrorToast message={error} onDismiss={dismissError} />
        </div>
      )}
    </div>
  );
}
