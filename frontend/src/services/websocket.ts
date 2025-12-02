import type { WebSocketMessage } from '../types/api';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private onConnectionChange?: (connected: boolean) => void;

  constructor(sessionId: string) {
    const wsBaseUrl = import.meta.env.VITE_WS_URL || `ws://${window.location.host}`;
    this.url = `${wsBaseUrl}/ws/sessions/${sessionId}`;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          this.onConnectionChange?.(true);
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.onConnectionChange?.(false);

          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private attemptReconnect(): void {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    setTimeout(() => {
      console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect().catch(console.error);
    }, delay);
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  send(type: string, data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = { type: type as any, data };
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }

  getWebSocket(): WebSocket | null {
    return this.ws;
  }

  // Event listeners
  on(eventType: string, callback: (data: any) => void): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(callback);
  }

  off(eventType: string, callback: (data: any) => void): void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      listeners.delete(callback);
    }
  }

  setConnectionChangeHandler(callback: (connected: boolean) => void): void {
    this.onConnectionChange = callback;
  }

  private handleMessage(message: WebSocketMessage): void {
    const listeners = this.listeners.get(message.type);
    if (listeners) {
      listeners.forEach(callback => callback(message.data));
    }

    // Also trigger generic 'message' listeners
    const messageListeners = this.listeners.get('message');
    if (messageListeners) {
      messageListeners.forEach(callback => callback(message));
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
