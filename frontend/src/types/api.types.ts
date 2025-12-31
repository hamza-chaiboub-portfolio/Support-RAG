export interface RetrievedChunk {
  chunk_id: number;
  asset_id: number;
  content: string;
  similarity_score: number;
  metadata: Record<string, unknown>;
}

export interface RagQueryRequest {
  project_id: number;
  query: string;
  n_results?: number;
  threshold?: number;
  max_tokens?: number;
  temperature?: number;
}

export interface RagQueryResponse {
  status: string;
  project_id: number;
  query: string;
  retrieved_chunks: RetrievedChunk[];
  retrieved_count: number;
  response: string;
  generation_status: string;
}

export interface ApiError {
  detail: string;
  status_code?: number;
  error_type?: string;
}

export interface GdprDeleteRequest {
  session_id: string;
  reason?: string;
}

export interface GdprDeleteResponse {
  message: string;
  status: 'success' | 'error';
  deleted_at?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
}
