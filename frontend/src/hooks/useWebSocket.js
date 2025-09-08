import { useState, useEffect, useRef, useCallback } from 'react';

const useWebSocket = (url, options = {}) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [lastMessage, setLastMessage] = useState(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = options.maxReconnectAttempts || 5;
  const reconnectInterval = options.reconnectInterval || 3000;

  const connect = useCallback(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      return;
    }

    // Prevent rapid reconnections
    if (reconnectTimeoutRef.current) {
      return;
    }

    try {
      const ws = new WebSocket(url);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
        
        // Send initial ping
        ws.send(JSON.stringify({ type: 'ping' }));
        
        if (options.onOpen) {
          options.onOpen(ws);
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          
          if (options.onMessage) {
            options.onMessage(data, ws);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
          setError('Failed to parse message');
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        
        if (options.onClose) {
          options.onClose(event);
        }

        // Attempt to reconnect if not a normal closure and not already reconnecting
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts && !reconnectTimeoutRef.current) {
          reconnectAttempts.current++;
          console.log(`Attempting to reconnect (${reconnectAttempts.current}/${maxReconnectAttempts})...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectTimeoutRef.current = null;
            connect();
          }, reconnectInterval);
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          setError('Max reconnection attempts reached');
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
        
        if (options.onError) {
          options.onError(error);
        }
      };

      setSocket(ws);
    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setError('Failed to create WebSocket connection');
    }
  }, [url, maxReconnectAttempts, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (socket) {
      socket.close(1000, 'User disconnected');
      setSocket(null);
    }
    
    setIsConnected(false);
    reconnectAttempts.current = 0;
  }, [socket]);

  const sendMessage = useCallback((message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      try {
        const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
        socket.send(messageStr);
        return true;
      } catch (err) {
        console.error('Error sending WebSocket message:', err);
        setError('Failed to send message');
        return false;
      }
    } else {
      console.warn('WebSocket is not connected');
      setError('WebSocket is not connected');
      return false;
    }
  }, [socket]);

  const sendPing = useCallback(() => {
    return sendMessage({ type: 'ping' });
  }, [sendMessage]);

  const subscribe = useCallback((events) => {
    return sendMessage({ type: 'subscribe', events });
  }, [sendMessage]);

  const unsubscribe = useCallback((events) => {
    return sendMessage({ type: 'unsubscribe', events });
  }, [sendMessage]);

  // Auto-connect on mount - only when URL changes
  useEffect(() => {
    if (url) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [url]); // Removed connect and disconnect from dependencies

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  return {
    socket,
    isConnected,
    error,
    lastMessage,
    connect,
    disconnect,
    sendMessage,
    sendPing,
    subscribe,
    unsubscribe
  };
};

export default useWebSocket;

