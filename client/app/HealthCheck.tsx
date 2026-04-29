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
          Last checked: {new Date(health.timestamp).toLocaleTimeString()}
        </p>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span>Embedding</span>
          <span>{getStatusIcon(health.services.embedding)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>LLM (Groq)</span>
          <span>{getStatusIcon(health.services.llm)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Cache (Redis)</span>
          <span>{getStatusIcon(health.services.cache)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Retriever (Pinecone)</span>
          <span>{getStatusIcon(health.services.retriever)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>gRPC Worker</span>
          <span>{getStatusIcon(health.services.grpc)}</span>
        </div>
      </div>
    </div>
  );
};

export default HealthCheck;
