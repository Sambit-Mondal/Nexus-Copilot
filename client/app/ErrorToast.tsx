/**
 * Error Toast Component
 * Displays error messages with smooth animations
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
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsExiting(true);
      setTimeout(onDismiss, 300);
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, onDismiss]);

  return (
    <div
      className={`p-4 bg-[#1a1a1a] border border-[rgba(239,68,68,0.3)] rounded-xl text-red-400 flex items-start gap-3 backdrop-blur-sm shadow-lg ${
        isExiting
          ? 'animate-slide-in-up opacity-0'
          : 'animate-slide-in-up'
      }`}
    >
      <span className="text-xl flex-shrink-0">❌</span>
      <div className="flex-1">
        <p className="font-medium text-sm">{message}</p>
      </div>
      <button
        onClick={() => {
          setIsExiting(true);
          setTimeout(onDismiss, 300);
        }}
        className="text-red-400/60 hover:text-red-400 text-xl transition-colors"
      >
        ×
      </button>
    </div>
  );
};

export default ErrorToast;
