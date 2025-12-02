import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sessionApi, executorApi } from '../services/api';
import type { CreateSessionRequest, JoinSessionRequest, UpdateProblemRequest, ExecuteCodeRequest } from '../types/api';

// Query keys
export const queryKeys = {
  sessions: ['sessions'] as const,
  session: (id: string) => ['session', id] as const,
  problem: (sessionId: string) => ['problem', sessionId] as const,
  executors: ['executors'] as const,
};

// Sessions
export const useSessions = () => {
  return useQuery({
    queryKey: queryKeys.sessions,
    queryFn: sessionApi.list,
  });
};

export const useSession = (sessionId: string) => {
  return useQuery({
    queryKey: queryKeys.session(sessionId),
    queryFn: () => sessionApi.get(sessionId),
    enabled: !!sessionId,
  });
};

export const useCreateSession = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateSessionRequest) => sessionApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.sessions });
    },
  });
};

export const useJoinSession = (sessionId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: JoinSessionRequest) => sessionApi.join(sessionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.session(sessionId) });
    },
  });
};

export const useDeleteSession = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => sessionApi.delete(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.sessions });
    },
  });
};

// Problem text
export const useProblem = (sessionId: string) => {
  return useQuery({
    queryKey: queryKeys.problem(sessionId),
    queryFn: () => sessionApi.getProblem(sessionId),
    enabled: !!sessionId,
  });
};

export const useUpdateProblem = (sessionId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProblemRequest) => sessionApi.updateProblem(sessionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.problem(sessionId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.session(sessionId) });
    },
  });
};

// Code execution
export const useExecuteCode = (sessionId: string) => {
  return useMutation({
    mutationFn: (data: ExecuteCodeRequest) => sessionApi.execute(sessionId, data),
  });
};

// Executors
export const useExecutors = () => {
  return useQuery({
    queryKey: queryKeys.executors,
    queryFn: executorApi.list,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
