/*
 * ShareDB hook for real-time collaborative editing in React.
 * Manages connection to ShareDB documents, handles local changes, and syncs remote changes.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

export interface ShareDBDocument {
  collection: string;
  doc_id: string;
  version: number;
  content: string;
}

export interface UseShareDBOptions {
  collection: string;
  doc_id: string;
  onRemoteChange?: (content: string) => void;
  onVersionChange?: (version: number) => void;
  autoSubscribe?: boolean;
}

export const useShareDB = (
  websocket: WebSocket | null,
  options: UseShareDBOptions
) => {
  const { collection, doc_id, onRemoteChange, onVersionChange, autoSubscribe = true } = options;

  const [content, setContent] = useState<string>('');
  const [version, setVersion] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubscribed, setIsSubscribed] = useState<boolean>(false);

  // Track if we've already subscribed to avoid duplicate subscriptions
  const hasSubscribed = useRef(false);
  const pendingChanges = useRef<{ position: number; type: string; content?: string }[]>([]);
  const lastKnownVersion = useRef<number>(0);

  // Fetch initial document state
  const fetchDocument = useCallback(async () => {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      websocket.send(
        JSON.stringify({
          type: 'fetch',
          collection,
          doc_id,
        })
      );
    } catch (err) {
      setError(`Failed to fetch document: ${err instanceof Error ? err.message : String(err)}`);
    }
  }, [websocket, collection, doc_id]);

  // Subscribe to document updates
  const subscribe = useCallback(async () => {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
      return;
    }

    if (hasSubscribed.current) {
      return;
    }

    try {
      websocket.send(
        JSON.stringify({
          type: 'subscribe',
          collection,
          doc_id,
        })
      );
      hasSubscribed.current = true;
      setIsSubscribed(true);
    } catch (err) {
      setError(`Failed to subscribe: ${err instanceof Error ? err.message : String(err)}`);
    }
  }, [websocket, collection, doc_id]);

  // Unsubscribe from document updates
  const unsubscribe = useCallback(async () => {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
      return;
    }

    try {
      websocket.send(
        JSON.stringify({
          type: 'unsubscribe',
          collection,
          doc_id,
        })
      );
      hasSubscribed.current = false;
      setIsSubscribed(false);
    } catch (err) {
      setError(`Failed to unsubscribe: ${err instanceof Error ? err.message : String(err)}`);
    }
  }, [websocket, collection, doc_id]);

  // Send a local change (insert or delete)
  const sendOperation = useCallback(
    async (type: 'insert' | 'delete', position: number, content?: string) => {
      if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        // Queue for later if not connected
        pendingChanges.current.push({ type, position, content });
        return false;
      }

      try {
        websocket.send(
          JSON.stringify({
            type: 'op',
            collection,
            doc_id,
            operation: {
              type,
              position,
              content,
              version: lastKnownVersion.current,
            },
          })
        );
        return true;
      } catch (err) {
        setError(`Failed to send operation: ${err instanceof Error ? err.message : String(err)}`);
        return false;
      }
    },
    [websocket, collection, doc_id]
  );

  // Get operation history
  const getHistory = useCallback(
    async (fromVersion: number = 0) => {
      if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        return;
      }

      try {
        websocket.send(
          JSON.stringify({
            type: 'history',
            collection,
            doc_id,
            from_version: fromVersion,
          })
        );
      } catch (err) {
        setError(`Failed to fetch history: ${err instanceof Error ? err.message : String(err)}`);
      }
    },
    [websocket, collection, doc_id]
  );

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (!websocket) {
      return;
    }

    const handleMessage = (event: MessageEvent) => {
      try {
        const message = JSON.parse(event.data);

        if (message.type === 'fetch-response') {
          if (message.collection === collection && message.doc_id === doc_id) {
            setContent(message.content);
            setVersion(message.version);
            lastKnownVersion.current = message.version;
            setIsLoading(false);
            setError(null);

            // Auto-subscribe after fetch if enabled
            if (autoSubscribe && !hasSubscribed.current) {
              subscribe();
            }
          }
        } else if (message.type === 'fetch-error') {
          setError(message.error);
          setIsLoading(false);
        } else if (message.type === 'subscribed') {
          if (message.collection === collection && message.doc_id === doc_id) {
            setIsSubscribed(true);
          }
        } else if (message.type === 'remote-op') {
          if (message.collection === collection && message.doc_id === doc_id) {
            const operation = message.operation;

            // Apply remote operation to local content
            if (operation.type === 'insert' && operation.content !== undefined) {
              setContent((prevContent) => {
                const newContent =
                  prevContent.slice(0, operation.position) +
                  operation.content +
                  prevContent.slice(operation.position);

                onRemoteChange?.(newContent);
                return newContent;
              });
            } else if (operation.type === 'delete') {
              setContent((prevContent) => {
                const length = operation.content ? operation.content.length : 1;
                const newContent =
                  prevContent.slice(0, operation.position) +
                  prevContent.slice(operation.position + length);

                onRemoteChange?.(newContent);
                return newContent;
              });
            }

            // Update version
            setVersion(operation.version);
            lastKnownVersion.current = operation.version;
            onVersionChange?.(operation.version);
          }
        } else if (message.type === 'op-ack') {
          if (message.collection === collection && message.doc_id === doc_id) {
            setVersion(message.version);
            lastKnownVersion.current = message.version;
            onVersionChange?.(message.version);

            // Send any pending changes
            if (pendingChanges.current.length > 0) {
              const pending = pendingChanges.current.shift();
              if (pending) {
                sendOperation(pending.type as 'insert' | 'delete', pending.position, pending.content);
              }
            }
          }
        } else if (message.type === 'history-response') {
          if (message.collection === collection && message.doc_id === doc_id) {
            // Handle operation history
            console.log('Received operation history:', message.operations);
          }
        }
      } catch (err) {
        console.error('Error handling WebSocket message:', err);
      }
    };

    websocket.addEventListener('message', handleMessage);

    return () => {
      websocket.removeEventListener('message', handleMessage);
    };
  }, [websocket, collection, doc_id, onRemoteChange, onVersionChange, autoSubscribe, subscribe, sendOperation]);

  // Initial fetch on mount
  useEffect(() => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      fetchDocument();
    }
  }, [websocket, fetchDocument]);

  // Send cursor/selection updates
  const sendCursor = useCallback(
    async (position: { line: number; column: number }, selection?: any) => {
      if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        return;
      }

      try {
        websocket.send(
          JSON.stringify({
            type: 'cursor',
            collection,
            doc_id,
            cursor: position,
            selection,
          })
        );
      } catch (err) {
        console.error(`Failed to send cursor: ${err instanceof Error ? err.message : String(err)}`);
      }
    },
    [websocket, collection, doc_id]
  );

  return {
    content,
    setContent,
    version,
    isLoading,
    error,
    isSubscribed,
    fetchDocument,
    subscribe,
    unsubscribe,
    sendOperation,
    getHistory,
    sendCursor,
  };
};
