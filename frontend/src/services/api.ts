import axios from 'axios';
import type {
  Session,
  CreateSessionRequest,
  JoinSessionRequest,
  UpdateProblemRequest,
  ExecuteCodeRequest,
  ExecutionResult,
  Executor
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

// Create axios instance with base configuration
export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Session API
export const sessionApi = {
  // Create a new session
  create: async (data: CreateSessionRequest): Promise<Session> => {
    const response = await apiClient.post<Session>('/sessions', data);
    return response.data;
  },

  // List all sessions
  list: async (): Promise<Session[]> => {
    const response = await apiClient.get<Session[]>('/sessions');
    return response.data;
  },

  // Get session by ID
  get: async (sessionId: string): Promise<Session> => {
    const response = await apiClient.get<Session>(`/sessions/${sessionId}`);
    return response.data;
  },

  // Join a session
  join: async (sessionId: string, data: JoinSessionRequest): Promise<User> => {
    const response = await apiClient.post<User>(`/sessions/${sessionId}/join`, data);
    return response.data;
  },

  // Update problem text (creator only)
  updateProblem: async (sessionId: string, data: UpdateProblemRequest): Promise<{ message: string }> => {
    const response = await apiClient.put<{ message: string }>(`/sessions/${sessionId}/problem`, data);
    return response.data;
  },

  // Get problem text
  getProblem: async (sessionId: string): Promise<{ problem_text: string }> => {
    const response = await apiClient.get<{ problem_text: string }>(`/sessions/${sessionId}/problem`);
    return response.data;
  },

  // Execute code
  execute: async (sessionId: string, data: ExecuteCodeRequest): Promise<ExecutionResult> => {
    const response = await apiClient.post<ExecutionResult>(`/sessions/${sessionId}/execute`, data);
    return response.data;
  },

  // Delete session
  delete: async (sessionId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(`/sessions/${sessionId}`);
    return response.data;
  },
};

// Executor API
export const executorApi = {
  // List supported executors
  list: async (): Promise<Executor[]> => {
    const response = await apiClient.get<{ executors: Executor[] }>('/executors');
    return response.data.executors;
  },
};

// Health check
export const healthApi = {
  check: async (): Promise<{ status: string }> => {
    const response = await apiClient.get<{ status: string }>('/health');
    return response.data;
  },
};
