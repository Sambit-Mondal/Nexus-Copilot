/**
 * Health Check Component
 * Displays API gateway service status
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
      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-500">Checking service status...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 rounded-lg border border-red-200">
        <p className="text-sm text-red-700">⚠️ {error}</p>
      </div>
    );
  }

  if (!health) {
    return null;
  }

  const getStatusIcon = (status: boolean) => (status ? '✅' : '❌');
  const getStatusColor = (status: string) => {
    if (status === 'healthy') return 'bg-green-50 border-green-200 text-green-700';
    if (status === 'degraded') return 'bg-yellow-50 border-yellow-200 text-yellow-700';
    return 'bg-red-50 border-red-200 text-red-700';
  };

  return (
    <div
      className={`p-4 rounded-lg border ${getStatusColor(health.status)}`}
    >
      <div className="mb-3">
        <p className="font-semibold text-sm">
          {health.status === 'healthy'
            ? '✅ All Services Healthy'
            : health.status === 'degraded'
              ? '⚠️ Degraded Service'
              : '❌ Service Error'}
        </p>
        <p className="text-xs opacity-75 mt-1">
          {health.timestamp && `Last checked: ${new Date(health.timestamp).toLocaleTimeString()}`}
        </p>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span>Redis Cache</span>
          <span>{getStatusIcon(health.redis === 'connected')}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>gRPC Worker</span>
          <span>{getStatusIcon(health.grpc === 'ready')}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Pinecone Retriever</span>
          <span>{getStatusIcon(health.pinecone === 'connected')}</span>
        </div>
      </div>
    </div>
  );
};

export default HealthCheck;
