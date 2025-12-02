export interface Session {
  id: string;
  name: string;
  language: string;
  problem_text?: string;
  created_at: string;
  expires_at: string;
  is_active: boolean;
  users?: User[];
}

export interface User {
  id: string;
  session_id: string;
  role: 'creator' | 'participant';
  joined_at: string;
  last_seen: string;
}

export interface CreateSessionRequest {
  name: string;
  language: string;
}

export interface JoinSessionRequest {
  user_id?: string;
}

export interface UpdateProblemRequest {
  user_id: string;
  problem_text: string;
}

export interface ExecuteCodeRequest {
  code: string;
  language: string;
}

export interface ExecutionResult {
  stdout: string;
  stderr: string;
  exit_code: number;
  execution_time_ms: number;
  memory_used_kb: number;
  error?: string;
}

export interface WebSocketMessage {
  type: 'user_joined' | 'user_left' | 'cursor_position' | 'problem_updated' | 'execution_started' | 'execution_completed';
  data: any;
}

export interface CursorPosition {
  line: number;
  column: number;
  user_id: string;
}

export interface Executor {
  language: string;
  display_name: string;
  description?: string;
}
