import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MainLayout } from '../Layout/MainLayout';
import { Header } from '../Layout/Header';
import { ProblemPanel } from '../Problem/ProblemPanel';
import { MonacoEditor } from '../Editor/MonacoEditor';
import { ExecutionOutput } from '../Output/ExecutionOutput';
import { useSession, useJoinSession, useExecuteCode, useProblem, useExecutors } from '../../hooks/useApi';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useShareDB } from '../../hooks/useShareDB';
import type { ExecutionResult, User } from '../../types/api';

export const SessionView: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  // State
  const [code, setCode] = useState(`# Write your solution here
def solution():
    pass

# Example usage:
# result = solution()
# print(result)`);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [problemText, setProblemText] = useState('**Welcome to your coding session!**\n\nClick the "Edit" button to add your problem statement here.\n\n### Instructions:\n1. Write your problem description\n2. Add examples and test cases\n3. Start coding!');

  // API hooks
  const { data: session, isLoading: sessionLoading } = useSession(sessionId!);
  const { data: problem } = useProblem(sessionId!);
  const { data: executors } = useExecutors();
  const joinSessionMutation = useJoinSession(sessionId!);
  const executeCodeMutation = useExecuteCode(sessionId!);

  // WebSocket - only connect when user is set
  const { isConnected, sendMessage, on, off, ws } = useWebSocket(currentUser ? sessionId! : '');

  // ShareDB for code synchronization
  const shareDB = useShareDB(ws || null, {
    collection: 'code',
    doc_id: sessionId || '',
    onRemoteChange: (newCode) => {
      setCode(newCode);
    },
    autoSubscribe: currentUser !== null,
  });

  // Initialize session and user
  useEffect(() => {
    if (!sessionId) {
      navigate('/');
      return;
    }

    // Auto-join as participant if not already joined
    if (session && !currentUser && !joinSessionMutation.isPending) {
      const storedUserId = localStorage.getItem(`session_${sessionId}_user`);
      const existingUser = session.users?.find(u => u.id === storedUserId);

      if (existingUser) {
        setCurrentUser(existingUser);
      } else {
        // Join as a new participant
        const role = 'participant';
        console.log('Joining session with role:', role);

        joinSessionMutation.mutate(
          {},
          {
            onSuccess: (returnedUser) => {
              // Use the actual user returned by the server
              console.log('Successfully joined with user:', returnedUser.id, 'role:', returnedUser.role);
              const user: User = {
                ...returnedUser,
                session_id: sessionId,
              };
              setCurrentUser(user);
              localStorage.setItem(`session_${sessionId}_user`, user.id);
            },
            onError: (error) => {
              console.error('Failed to join session:', error);
            }
          }
        );
      }
    }
  }, [sessionId, session, currentUser, navigate]); // Removed joinSessionMutation from deps to prevent loop

  // Update problem text when loaded
  useEffect(() => {
    if (problem?.problem_text) {
      setProblemText(problem.problem_text);
    }
  }, [problem]);

  // WebSocket event listeners
  useEffect(() => {
    if (!isConnected) return;

    const handleUserJoined = (data: { user: User }) => {
      console.log('User joined:', data.user);
      // Update current user if it's us
      const storedUserId = localStorage.getItem(`session_${sessionId}_user`);
      if (!storedUserId || storedUserId === data.user.id) {
        setCurrentUser(data.user);
        localStorage.setItem(`session_${sessionId}_user`, data.user.id);
      }
    };

    const handleUserLeft = (data: { user_id: string }) => {
      console.log('User left:', data.user_id);
    };

    const handleProblemUpdated = (data: { problem_text: string }) => {
      setProblemText(data.problem_text);
    };

    const handleCursorPosition = (data: { line: number; column: number; user_id: string }) => {
      // Handle cursor position updates from other users
      console.log('Cursor position:', data);
    };

    on('user_joined', handleUserJoined);
    on('user_left', handleUserLeft);
    on('problem_updated', handleProblemUpdated);
    on('cursor_position', handleCursorPosition);

    return () => {
      off('user_joined', handleUserJoined);
      off('user_left', handleUserLeft);
      off('problem_updated', handleProblemUpdated);
      off('cursor_position', handleCursorPosition);
    };
  }, [isConnected, on, off, sessionId]);

  // Handlers
  const handleCodeChange = (newCode: string) => {
    setCode(newCode);
  };

  const handleCursorChange = (line: number, column: number) => {
    if (isConnected) {
      sendMessage('cursor_position', { line, column });
    }
  };

  const handleRunCode = async () => {
    if (!session || isExecuting) return;

    setIsExecuting(true);
    setExecutionResult(null);

    try {
      const result = await executeCodeMutation.mutateAsync({
        code,
        language: session.language,
      });
      setExecutionResult(result);
    } catch (error) {
      console.error('Execution failed:', error);
      setExecutionResult({
        stdout: '',
        stderr: '',
        exit_code: -1,
        execution_time_ms: 0,
        memory_used_kb: 0,
        error: 'Failed to execute code. Please try again.',
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const handleLanguageChange = (language: string) => {
    // Language changes would require session update API
    console.log('Language change requested:', language);
  };

  const handleProblemUpdate = (text: string) => {
    setProblemText(text);
  };

  // Loading state
  if (sessionLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-gray-300 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading session...</p>
        </div>
      </div>
    );
  }

  // Session not found
  if (!session) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="text-4xl mb-4">🔍</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Session Not Found</h1>
          <p className="text-gray-600 mb-4">The session you're looking for doesn't exist or has expired.</p>
          <button
            onClick={() => navigate('/')}
            className="btn-primary"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  // Allow everyone to edit - remove role restrictions
  const isCreator = true; // Everyone can edit
  const shareUrl = `${window.location.origin}/session/${sessionId}`;
  const supportedLanguages = executors?.map(e => e.language) || [session.language];

  return (
    <MainLayout
      header={
        <Header
          sessionName={session?.name}
          language={session.language}
          onLanguageChange={handleLanguageChange}
          onRunCode={handleRunCode}
          isRunning={isExecuting}
          shareUrl={shareUrl}
          userCount={session?.users?.length || 1}
          supportedLanguages={supportedLanguages}
          currentUserRole={currentUser?.role}
        />
      }
      problemPanel={
        <ProblemPanel
          sessionId={sessionId!}
          problemText={problemText}
          isCreator={isCreator}
          currentUserId={currentUser?.id}
          onProblemUpdate={handleProblemUpdate}
          sendOperation={shareDB.sendOperation}
        />
      }
      codeEditor={
        <MonacoEditor
          value={code}
          language={session.language}
          onChange={handleCodeChange}
          onCursorChange={handleCursorChange}
          onRemoteChange={shareDB.onRemoteChange ? undefined : undefined}
          theme="vs"
          readOnly={false}
          shareDBEnabled={true}
          sendOperation={shareDB.sendOperation}
          sendCursor={shareDB.sendCursor}
        />
      }
      outputPanel={
        <ExecutionOutput
          result={executionResult || undefined}
          isRunning={isExecuting}
          error={executeCodeMutation.error?.message}
        />
      }
    />
  );
};
