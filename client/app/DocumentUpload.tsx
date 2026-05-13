'use client';

import React, { useState, useRef, useCallback } from 'react';
import { UploadProgress } from './types';

interface DocumentUploadProps {
  onUploadStart: (filename: string) => void;
  onUploadProgress: (progress: UploadProgress) => void;
  onUploadComplete: (documentId: string) => void;
  onError: (error: string) => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadStart,
  onUploadProgress,
  onUploadComplete,
  onError,
}) => {
  const [uploads, setUploads] = useState<Map<string, UploadProgress>>(new Map());
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dragRef = useRef<HTMLDivElement>(null);

  const uploadFile = useCallback(
    async (file: File) => {
      if (!file.type.includes('pdf')) {
        onError('Please upload a PDF file');
        return;
      }

      const maxSize = 50 * 1024 * 1024; // 50MB
      if (file.size > maxSize) {
        onError('File size exceeds 50MB limit');
        return;
      }

      const fileKey = `${Date.now()}_${file.name}`;
      onUploadStart(file.name);

      const progress: UploadProgress = {
        documentId: fileKey,
        filename: file.name,
        status: 'uploading',
        progress: 0,
      };

      setUploads((prev) => new Map(prev).set(fileKey, progress));

      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('client_id', 'nexus-client');
        formData.append('document_type', 'pdf');

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        // Start upload
        const response = await fetch(`${apiUrl}/api/v1/upload`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }

        const data = await response.json();

        // Update progress
        const updatedProgress: UploadProgress = {
          documentId: data.upload_id,
          filename: file.name,
          status: 'processing',
          progress: 50,
        };

        setUploads((prev) => new Map(prev).set(fileKey, updatedProgress));
        onUploadProgress(updatedProgress);

        // Poll for processing completion
        await pollProcessingStatus(
          data.upload_id,
          fileKey,
          file.name,
          onUploadProgress,
          setUploads
        );

        onUploadComplete(data.upload_id);
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Upload failed';
        onError(errorMessage);

        setUploads((prev) => {
          const updated = new Map(prev);
          const current = updated.get(fileKey);
          if (current) {
            current.status = 'failed';
            current.error = errorMessage;
          }
          return updated;
        });
      }
    },
    [onUploadStart, onUploadProgress, onUploadComplete, onError]
  );

  const pollProcessingStatus = async (
    documentId: string,
    fileKey: string,
    filename: string,
    onProgress: (progress: UploadProgress) => void,
    setUploads: React.Dispatch<React.SetStateAction<Map<string, UploadProgress>>>
  ) => {
    let attempts = 0;
    const maxAttempts = 30; // 5 minutes with 10-second intervals

    while (attempts < maxAttempts) {
      await new Promise((resolve) => setTimeout(resolve, 10000)); // Wait 10 seconds
      attempts++;

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/upload/${documentId}/status`);

        if (response.ok) {
          const data = await response.json();

          const progress: UploadProgress = {
            documentId,
            filename,
            status: data.status,
            progress: data.progress?.percent ?? (75 + Math.min(attempts / maxAttempts * 25, 24)),
          };

          setUploads((prev) => new Map(prev).set(fileKey, progress));
          onProgress(progress);

          if (data.status === 'completed') {
            return;
          }
        }
      } catch (error) {
        console.error('Status check failed:', error);
      }
    }

    // Mark as completed if polling finished
    setUploads((prev) => {
      const updated = new Map(prev);
      const current = updated.get(fileKey);
      if (current) {
        current.status = 'completed';
        current.progress = 100;
      }
      return updated;
    });
  };

  const handleFileSelect = useCallback(
    (files: FileList | null) => {
      if (!files) return;

      Array.from(files).forEach((file) => {
        uploadFile(file);
      });
    },
    [uploadFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (dragRef.current) {
      dragRef.current.classList.add('bg-blue-50', 'border-blue-400');
    }
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (dragRef.current) {
      dragRef.current.classList.remove('bg-blue-50', 'border-blue-400');
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      if (dragRef.current) {
        dragRef.current.classList.remove('bg-blue-50', 'border-blue-400');
      }
      handleFileSelect(e.dataTransfer.files);
    },
    [handleFileSelect]
  );

  return (
    <div className="flex flex-col h-full bg-white overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900">Documents</h2>
        <p className="text-sm text-gray-500 mt-1">
          Upload PDFs to include in your analysis
        </p>
      </div>

      {/* Upload Area */}
      <div className="flex-shrink-0 p-6 border-b border-gray-200">
        <div
          ref={dragRef}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer transition hover:border-blue-400 hover:bg-blue-50"
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="space-y-2">
            <div className="text-3xl">📁</div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                Drag & drop your PDFs
              </p>
              <p className="text-xs text-gray-500 mt-1">
                or click to select files
              </p>
            </div>
            <p className="text-xs text-gray-400">
              Max 50MB per file. PDF format only.
            </p>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf"
            onChange={(e) => handleFileSelect(e.target.files)}
            className="hidden"
          />
        </div>
      </div>

      {/* Uploads List */}
      <div className="flex-1 overflow-y-auto p-6">
        {uploads.size === 0 ? (
          <div className="text-center text-gray-400 py-8">
            <p className="text-sm">No documents uploaded yet</p>
          </div>
        ) : (
          <div className="space-y-4">
            {Array.from(uploads.entries()).map(([key, upload]) => (
              <div
                key={key}
                className="p-4 border border-gray-200 rounded-lg bg-gray-50"
              >
                {/* Filename and Status */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {upload.filename}
                    </p>
                    <p className="text-xs text-gray-500 mt-1 capitalize">
                      {upload.status === 'completed' && '✅ Ready to use'}
                      {upload.status === 'processing' && '⏳ Processing...'}
                      {upload.status === 'uploading' && '📤 Uploading...'}
                      {upload.status === 'failed' && `❌ ${upload.error}`}
                    </p>
                  </div>
                  <span className="text-xs text-gray-500 ml-2">
                    {Math.round(upload.progress)}%
                  </span>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      upload.status === 'failed'
                        ? 'bg-red-500'
                        : upload.status === 'completed'
                          ? 'bg-green-500'
                          : 'bg-blue-500'
                    }`}
                    style={{ width: `${upload.progress}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUpload;
