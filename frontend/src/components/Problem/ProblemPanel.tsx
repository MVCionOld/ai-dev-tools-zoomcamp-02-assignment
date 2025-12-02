import React, { useState, useCallback } from 'react';
import { ProblemViewer } from './ProblemViewer';
import { ProblemEditor } from './ProblemEditor';
import { useUpdateProblem } from '../../hooks/useApi';

interface ProblemPanelProps {
  sessionId: string;
  problemText: string;
  isCreator: boolean;
  currentUserId?: string;
  onProblemUpdate?: (text: string) => void;
  sendOperation?: (type: 'insert' | 'delete', position: number, content?: string) => Promise<boolean>;
}

export const ProblemPanel: React.FC<ProblemPanelProps> = ({
  sessionId,
  problemText,
  isCreator,
  currentUserId,
  onProblemUpdate,
  sendOperation,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const updateProblemMutation = useUpdateProblem(sessionId);

  const handleStartEdit = () => {
    // Allow everyone to edit - removed role check
    setIsEditing(true);
  };

  const handleSave = useCallback(async (newText: string) => {
    try {
      if (!currentUserId) {
        alert('User ID not available. Please refresh and try again.');
        return;
      }
      console.log('Saving problem text:', { sessionId, currentUserId, newText });

      // Send update via ShareDB if available
      if (sendOperation && newText !== problemText) {
        // Calculate the difference and send operations
        const insertText = newText.substring(problemText.length);
        if (insertText) {
          await sendOperation('insert', problemText.length, insertText);
        }
      }

      // Also update via REST API for persistence
      const result = await updateProblemMutation.mutateAsync({
        user_id: currentUserId,
        problem_text: newText
      });
      console.log('Save successful:', result);
      onProblemUpdate?.(newText);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update problem:', error);
      // Show error but keep editing mode so user can retry
      if (error instanceof Error) {
        alert(`Failed to save: ${error.message}`);
      } else {
        alert('Failed to save changes. Please try again.');
      }
    }
  }, [currentUserId, sessionId, problemText, updateProblemMutation, onProblemUpdate, sendOperation]);

  const handleCancel = () => {
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <ProblemEditor
        initialValue={problemText}
        onSave={handleSave}
        onCancel={handleCancel}
        isSaving={updateProblemMutation.isPending}
      />
    );
  }

  return (
    <ProblemViewer
      problemText={problemText}
      isCreator={isCreator}
      onEdit={handleStartEdit}
    />
  );
};
