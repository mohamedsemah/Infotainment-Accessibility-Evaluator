import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import useWebSocket from '../hooks/useWebSocket';
import useAppStore from '../store/useAppStore';

const ProgressContext = createContext();

const progressReducer = (state, action) => {
  switch (action.type) {
    case 'CONNECT':
      return {
        ...state,
        isConnected: true,
        error: null
      };
    case 'DISCONNECT':
      return {
        ...state,
        isConnected: false
      };
    case 'ERROR':
      return {
        ...state,
        error: action.payload
      };
    case 'PROGRESS_UPDATE':
      return {
        ...state,
        lastUpdate: action.payload,
        updates: [...state.updates, action.payload].slice(-20) // Keep last 20 updates only
      };
    case 'AGENT_START':
      return {
        ...state,
        activeAgents: [...state.activeAgents, action.payload],
        lastUpdate: action.payload
      };
    case 'AGENT_COMPLETE':
      return {
        ...state,
        activeAgents: state.activeAgents.filter(agent => agent.agent_name !== action.payload.agent_name),
        completedAgents: [...state.completedAgents, action.payload].slice(-10), // Keep last 10 completed agents
        lastUpdate: action.payload
      };
    case 'AGENT_ERROR':
      return {
        ...state,
        activeAgents: state.activeAgents.filter(agent => agent.agent_name !== action.payload.agent_name),
        errorAgents: [...state.errorAgents, action.payload].slice(-5), // Keep last 5 error agents
        lastUpdate: action.payload
      };
    case 'ANALYSIS_START':
      return {
        ...state,
        isAnalyzing: true,
        activeAgents: [],
        completedAgents: [],
        errorAgents: [],
        lastUpdate: action.payload
      };
    case 'ANALYSIS_COMPLETE':
      return {
        ...state,
        isAnalyzing: false,
        lastUpdate: action.payload
      };
    case 'CLEAR':
      return {
        ...state,
        activeAgents: [],
        completedAgents: [],
        errorAgents: [],
        updates: [],
        lastUpdate: null
      };
    default:
      return state;
  }
};

const initialState = {
  isConnected: false,
  error: null,
  isAnalyzing: false,
  activeAgents: [],
  completedAgents: [],
  errorAgents: [],
  updates: [],
  lastUpdate: null
};

export const ProgressProvider = ({ children }) => {
  const [state, dispatch] = useReducer(progressReducer, initialState);
  const { uploadId, setAgentStatus, setRunningAgents, setCompletedAgents } = useAppStore();

  const wsUrl = uploadId ? `ws://localhost:8000/api/progress?upload_id=${uploadId}` : null;

  // Stable callback references to prevent re-connections
  const handleWebSocketMessage = useCallback((data) => {
    switch (data.event_type) {
      case 'analysis_start':
        dispatch({ type: 'ANALYSIS_START', payload: data });
        setAgentStatus('running');
        break;
      case 'analysis_complete':
        dispatch({ type: 'ANALYSIS_COMPLETE', payload: data });
        setAgentStatus('success');
        break;
      case 'agent_start':
        dispatch({ type: 'AGENT_START', payload: data });
        setRunningAgents(prev => [...prev, data.agent_name]);
        break;
      case 'agent_progress':
        dispatch({ type: 'PROGRESS_UPDATE', payload: data });
        break;
      case 'agent_complete':
        dispatch({ type: 'AGENT_COMPLETE', payload: data });
        setRunningAgents(prev => prev.filter(agent => agent !== data.agent_name));
        setCompletedAgents(prev => [...prev, data.agent_name]);
        break;
      case 'agent_error':
        dispatch({ type: 'AGENT_ERROR', payload: data });
        setRunningAgents(prev => prev.filter(agent => agent !== data.agent_name));
        break;
      case 'clustering_start':
      case 'clustering_complete':
      case 'patch_generation_start':
      case 'patch_generation_complete':
        dispatch({ type: 'PROGRESS_UPDATE', payload: data });
        break;
      default:
        dispatch({ type: 'PROGRESS_UPDATE', payload: data });
    }
  }, [setAgentStatus, setRunningAgents, setCompletedAgents]);

  const handleWebSocketOpen = useCallback(() => {
    dispatch({ type: 'CONNECT' });
    console.log('Progress WebSocket connected');
  }, []);

  const handleWebSocketClose = useCallback(() => {
    dispatch({ type: 'DISCONNECT' });
    console.log('Progress WebSocket disconnected');
  }, []);

  const handleWebSocketError = useCallback((error) => {
    dispatch({ type: 'ERROR', payload: error.message || 'WebSocket error' });
    console.error('Progress WebSocket error:', error);
  }, []);

  const { isConnected, error, lastMessage, sendMessage } = useWebSocket(wsUrl, {
    onOpen: handleWebSocketOpen,
    onClose: handleWebSocketClose,
    onError: handleWebSocketError,
    onMessage: handleWebSocketMessage
  });


  const clearProgress = useCallback(() => {
    dispatch({ type: 'CLEAR' });
  }, []);

  // Memory cleanup - clear old data periodically
  useEffect(() => {
    const cleanupInterval = setInterval(() => {
      if (state.updates.length > 50 || state.completedAgents.length > 20) {
        dispatch({ type: 'CLEAR' });
      }
    }, 30000); // Cleanup every 30 seconds

    return () => clearInterval(cleanupInterval);
  }, [state.updates.length, state.completedAgents.length]);

  const subscribeToEvents = (events) => {
    if (isConnected) {
      sendMessage({ type: 'subscribe', events });
    }
  };

  const unsubscribeFromEvents = (events) => {
    if (isConnected) {
      sendMessage({ type: 'unsubscribe', events });
    }
  };

  const sendPing = () => {
    if (isConnected) {
      sendMessage({ type: 'ping' });
    }
  };

  // Auto-subscribe to all events when connected (only once)
  useEffect(() => {
    if (isConnected) {
      subscribeToEvents([
        'analysis_start',
        'analysis_complete',
        'agent_start',
        'agent_progress',
        'agent_complete',
        'agent_error',
        'clustering_start',
        'clustering_complete',
        'patch_generation_start',
        'patch_generation_complete'
      ]);
    }
  }, [isConnected, subscribeToEvents]);

  const value = {
    ...state,
    isConnected,
    error,
    clearProgress,
    subscribeToEvents,
    unsubscribeFromEvents,
    sendPing,
    lastMessage
  };

  return (
    <ProgressContext.Provider value={value}>
      {children}
    </ProgressContext.Provider>
  );
};

export const useProgress = () => {
  const context = useContext(ProgressContext);
  if (!context) {
    throw new Error('useProgress must be used within a ProgressProvider');
  }
  return context;
};

export default ProgressContext;

