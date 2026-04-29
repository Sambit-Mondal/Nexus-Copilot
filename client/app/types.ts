/**
 * API Types
 */

export interface QueryRequest {
  query: string;
  session_id: string;
  stream?: boolean;
}

export interface QueryResponse {
  response: string;
  sources?: Citation[];
  session_id: string;
  timestamp: string;
}

export interface Citation {
  document_id: string;
  filename: string;
  page_number?: number;
  confidence: number;
}

export interface IngestRequest {
  client_id: string;
  document_type?: string;
}

export interface IngestResponse {
  document_id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
}

export interface StreamingChunk {
  chunk: string;
  citations?: Citation[];
  isComplete?: boolean;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  services: {
    embedding: boolean;
    llm: boolean;
    cache: boolean;
    retriever: boolean;
    grpc: boolean;
  };
  timestamp: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

export interface ConversationSession {
  id: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface UploadProgress {
  documentId: string;
  filename: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  error?: string;
}
