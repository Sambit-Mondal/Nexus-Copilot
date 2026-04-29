/**
 * Error Toast Component
 * Displays error messages to the user
 */

import React, { useState, useEffect } from 'react';

interface ErrorToastProps {
  message: string;
  duration?: number;
  onDismiss: () => void;
}

export const ErrorToast: React.FC<ErrorToastProps> = ({
  message,
  duration = 5000,
  onDismiss,
}) => {
  useEffect(() => {
    const timer = setTimeout(onDismiss, duration);
    return () => clearTimeout(timer);
  }, [duration, onDismiss]);

  return (
    <div className="animate-in slide-in-from-top fade-in p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-start gap-3">
      <span className="text-xl flex-shrink-0">❌</span>
      <div className="flex-1">
        <p className="font-medium text-sm">{message}</p>
      </div>
      <button
        onClick={onDismiss}
        className="text-red-400 hover:text-red-600 text-xl"
      >
        ×
      </button>
    </div>
  );
};

export default ErrorToast;
