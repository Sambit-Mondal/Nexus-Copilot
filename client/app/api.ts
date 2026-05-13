/**
 * Utility functions for streaming responses from the API
 * Handles EventSource API for Server-Sent Events (SSE)
 */

import { Citation, StreamingChunk } from './types';

export interface StreamConfig {
  onChunk: (chunk: string) => void;
  onCitation: (citations: Citation[]) => void;
  onComplete: () => void;
  onError: (error: Error) => void;
  signal?: AbortSignal;
}

/**
 * Stream responses from the /query endpoint using EventSource API
 * Handles the "typing" effect by appending chunks in real-time
 */
export function streamQuery(
  sessionId: string,
  query: string,
  config: StreamConfig
): void {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const queryParams = new URLSearchParams({
    query,
    session_id: sessionId,
    stream: 'true',
  });

  const eventSource = new EventSource(`${apiUrl}/api/v1/query?${queryParams}`);

  // Handle abort signal
  if (config.signal) {
    config.signal.addEventListener('abort', () => {
      eventSource.close();
      config.onComplete();
    });
  }

  eventSource.addEventListener('chunk', (event: Event) => {
    try {
      const typedEvent = event as MessageEvent;
      const data = JSON.parse(typedEvent.data) as StreamingChunk;
      config.onChunk(data.chunk);

      if (data.citations && data.citations.length > 0) {
        config.onCitation(data.citations);
      }

      if (data.isComplete) {
        eventSource.close();
        config.onComplete();
      }
    } catch (error) {
      console.error('Failed to parse chunk:', error, 'data:', (event as MessageEvent).data);
      config.onError(
        new Error(`Failed to parse streaming response: ${error}`)
      );
    }
  });

  // Fallback: also listen to generic 'message' events
  eventSource.addEventListener('message', (event: Event) => {
    try {
      const typedEvent = event as MessageEvent;
      const data = JSON.parse(typedEvent.data) as StreamingChunk;
      config.onChunk(data.chunk);

      if (data.citations && data.citations.length > 0) {
        config.onCitation(data.citations);
      }

      if (data.isComplete) {
        eventSource.close();
        config.onComplete();
      }
    } catch (error) {
      // Ignore parse errors for message events
    }
  });

  eventSource.addEventListener('citations', (event: Event) => {
    try {
      const typedEvent = event as MessageEvent;
      const data = JSON.parse(typedEvent.data);
      if (data.sources && Array.isArray(data.sources)) {
        config.onCitation(data.sources);
      }
    } catch (error) {
      console.error('Failed to parse citations:', error);
    }
  });

  eventSource.addEventListener('error', (event: Event) => {
    eventSource.close();
    const typedEvent = event as MessageEvent;
    config.onError(
      new Error(`Streaming error: ${typedEvent.data || 'Unknown error'}`)
    );
  });

  eventSource.addEventListener('done', () => {
    eventSource.close();
    config.onComplete();
  });
}

/**
 * Fetch with streaming support using ReadableStream
 * Alternative to EventSource for more control
 */
export async function streamQueryFetch(
  sessionId: string,
  query: string,
  config: StreamConfig
): Promise<void> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  try {
    const response = await fetch(`${apiUrl}/api/v1/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
      },
      body: JSON.stringify({
        query,
        session_id: sessionId,
        stream: true,
      }),
      signal: config.signal,
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is not readable');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        config.onComplete();
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');

      // Process complete lines
      for (let i = 0; i < lines.length - 1; i++) {
        const line = lines[i].trim();

        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6)) as StreamingChunk;
            config.onChunk(data.chunk);

            if (data.citations && data.citations.length > 0) {
              config.onCitation(data.citations);
            }

            if (data.isComplete) {
              config.onComplete();
              reader.cancel();
              return;
            }
          } catch (error) {
            console.error('Failed to parse chunk:', error);
          }
        }
      }

      // Keep incomplete line in buffer
      buffer = lines[lines.length - 1];
    }
  } catch (error) {
    if (error instanceof Error && error.name !== 'AbortError') {
      config.onError(error);
    }
  }
}

/**
 * Parse streaming response for citations in final chunk
 */
export function parseCitations(responseText: string): Citation[] {
  const citationMatch = responseText.match(
    /\[CITATIONS\]([\s\S]*?)\[\/CITATIONS\]/
  );
  if (!citationMatch) return [];

  try {
    return JSON.parse(citationMatch[1]);
  } catch {
    return [];
  }
}

/**
 * Generate unique session ID for conversation
 */
export function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
