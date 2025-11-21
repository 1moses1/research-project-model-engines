import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8006';

export const useWebSocket = () => {
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Initialize Socket.IO connection
    socketRef.current = io(WS_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    });

    socketRef.current.on('connect', () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    });

    socketRef.current.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    });

    socketRef.current.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      setIsConnected(false);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  const subscribe = (event: string, callback: (data: any) => void) => {
    if (socketRef.current) {
      socketRef.current.on(event, callback);
    }

    // Return unsubscribe function
    return () => {
      if (socketRef.current) {
        socketRef.current.off(event, callback);
      }
    };
  };

  const emit = (event: string, data: any) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit(event, data);
    }
  };

  return {
    isConnected,
    subscribe,
    emit,
    socket: socketRef.current
  };
};
