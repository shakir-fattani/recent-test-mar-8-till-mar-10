// Common API response types

// Auth types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_superuser: boolean;
}

// Chat types
export interface ChatMessage {
  id: string;
  chat_id: string;
  role: string;
  message: string;
  extra_data?: Record<string, string>;
  created_at: string;
}

export interface Chat {
  chat_id: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  first_message?: string;
  first_role?: string;
  history?: ChatMessage[];
}

// File types
export interface FileInfo {
  id: string;
  file_name: string;
  file_type: string;
  file_size: string;
  file_path: string;
  file_checksum: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

// Error response
export interface ApiError {
  detail: string;
}
