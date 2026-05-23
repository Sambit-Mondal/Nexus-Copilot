/**
 * Health Check Component
 * Displays API gateway service status in a minimal, modern style
 */

import React, { useState, useEffect } from 'react';
import { HealthCheckResponse } from './types';

interface HealthCheckProps {
  apiUrl?: string;
}

export const HealthCheck: React.FC<HealthCheckProps> = ({
  apiUrl = 'http://localhost:8000',
}) => {
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${apiUrl}/health`);
        if (!response.ok) {
          throw new Error(`Health check failed: ${response.statusText}`);
        }
        const data = await response.json();
        setHealth(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Health check failed');
        setHealth(null);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, [apiUrl]);

  if (loading) {
    return (
      <div className="p-4 bg-[#1a1a1a] rounded-lg border border-[rgba(255,255,255,0.08)]">
        <p className="text-sm text-gray-400 animate-pulse">Checking service status...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-[#1a1a1a] rounded-lg border border-[rgba(239,68,68,0.3)]">
        <p className="text-sm text-red-400">⚠️ Service unavailable</p>
      </div>
    );
  }

  if (!health) {
    return null;
  }

  const getStatusDot = (status: string) => {
    switch (status) {
      case 'connected':
      case 'ready':
        return '🟢';
      case 'disconnected':
      case 'error':
        return '🔴';
      default:
        return '🟡';
    }
  };

  return (
    <div className="p-4 rounded-lg border border-[rgba(255,255,255,0.08)] bg-[#1a1a1a]">
      <p className="text-xs font-semibold text-gray-300 mb-3">Service Status</p>
      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Redis</span>
          <span className="text-xl">{getStatusDot(health.redis)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">gRPC</span>
          <span className="text-xl">{getStatusDot(health.grpc)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Pinecone</span>
          <span className="text-xl">{getStatusDot(health.pinecone)}</span>
        </div>
      </div>
    </div>
  );
};

export default HealthCheck;
