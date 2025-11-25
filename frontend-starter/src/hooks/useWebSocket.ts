import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { WebSocketMessage, WebSocketMessageType } from '@/types';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

interface UseWebSocketReturn {
  socket: Socket | null;
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  lastMessage: WebSocketMessage | null;
  send: (message: WebSocketMessage) => void;
  disconnect: () => void;
  reconnect: () => void;
}

export const useWebSocket = (
  url: string = 'ws://localhost:8080/ws',
  options: UseWebSocketOptions = {}
): UseWebSocketReturn => {
  const {
    autoConnect = true,
    reconnectAttempts = 5,
    reconnectDelay = 5000,
  } = options;

  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectCountRef = useRef(0);
  const socketRef = useRef<Socket | null>(null);

  const connect = useCallback(() => {
    if (isConnecting || (socketRef.current && socketRef.current.connected)) {
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      // Create WebSocket connection
      const newSocket = io(url, {
        transports: ['websocket'],
        upgrade: false,
        rememberUpgrade: false,
      });

      socketRef.current = newSocket;
      setSocket(newSocket);

      newSocket.on('connect', () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setIsConnecting(false);
        setError(null);
        reconnectCountRef.current = 0;
      });

      newSocket.on('disconnect', (reason) => {
        console.log('WebSocket disconnected:', reason);
        setIsConnected(false);
        setIsConnecting(false);

        if (reason === 'io server disconnect') {
          // Server initiated disconnect, don't reconnect
          return;
        }

        // Attempt to reconnect
        if (reconnectCountRef.current < reconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectCountRef.current++;
            console.log(`Reconnection attempt ${reconnectCountRef.current}/${reconnectAttempts}`);
            connect();
          }, reconnectDelay);
        } else {
          setError('Failed to reconnect after maximum attempts');
        }
      });

      newSocket.on('connect_error', (err) => {
        console.error('WebSocket connection error:', err);
        setError(err.message);
        setIsConnecting(false);
      });

      newSocket.on('message', (data: WebSocketMessage) => {
        setLastMessage(data);
      });

      // Handle raw message events for compatibility
      newSocket.on('data', (data: any) => {
        try {
          const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
          setLastMessage(parsedData);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      });

    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      setIsConnecting(false);
    }
  }, [url, isConnecting, reconnectAttempts, reconnectDelay]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }

    setSocket(null);
    setIsConnected(false);
    setIsConnecting(false);
    reconnectCountRef.current = 0;
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectCountRef.current = 0;
    setTimeout(connect, 1000);
  }, [disconnect, connect]);

  const send = useCallback((message: WebSocketMessage) => {
    if (socketRef.current && socketRef.current.connected) {
      socketRef.current.emit('message', message);
    } else {
      console.warn('Cannot send message: WebSocket not connected');
      setError('Cannot send message: WebSocket not connected');
    }
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Handle page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Page hidden, optionally pause updates
      } else if (!isConnected && !isConnecting) {
        // Page visible and not connected, attempt to reconnect
        reconnect();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isConnected, isConnecting, reconnect]);

  return {
    socket,
    isConnected,
    isConnecting,
    error,
    lastMessage,
    send,
    disconnect,
    reconnect,
  };
};