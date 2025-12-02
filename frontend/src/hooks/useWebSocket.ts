import { useEffect, useRef, useState } from 'react';
import { WebSocketService } from '../services/websocket';
import type { WebSocketMessage } from '../types/api';

export const useWebSocket = (sessionId: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const wsRef = useRef<WebSocketService | null>(null);

  useEffect(() => {
    if (!sessionId || sessionId.trim() === '') return;

    // Create WebSocket service
    wsRef.current = new WebSocketService(sessionId);

    // Set connection change handler
    wsRef.current.setConnectionChangeHandler((connected) => {
      setIsConnected(connected);
      if (connected) {
        setWs(wsRef.current?.getWebSocket() || null);
      }
    });

    // Connect
    wsRef.current.connect().catch(console.error);

    // Cleanup on unmount
    return () => {
      wsRef.current?.disconnect();
      wsRef.current = null;
      setIsConnected(false);
      setWs(null);
    };
  }, [sessionId]);

  const sendMessage = (type: string, data: any) => {
    wsRef.current?.send(type, data);
  };

  const on = (eventType: string, callback: (data: any) => void) => {
    wsRef.current?.on(eventType, callback);
  };

  const off = (eventType: string, callback: (data: any) => void) => {
    wsRef.current?.off(eventType, callback);
  };

  // Listen to all messages for debugging/logging
  useEffect(() => {
    if (!wsRef.current) return;

    const handleMessage = (message: WebSocketMessage) => {
      setLastMessage(message);
    };

    wsRef.current.on('message', handleMessage);

    return () => {
      wsRef.current?.off('message', handleMessage);
    };
  }, []);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    on,
    off,
    ws,
  };
};
