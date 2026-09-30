import React, { createContext, useContext, useEffect, useState, useRef, useCallback } from 'react';

const RealtimeContext = createContext(null);

export const RealtimeProvider = ({ children }) => {
  const [status, setStatus] = useState('CONNECTED'); // CONNECTED | CONNECTING | DISCONNECTED
  const listenersRef = useRef(new Map()); // eventId -> Set of callback functions
  const socketRef = useRef(null);

  // Subscribe to updates for a specific event
  const subscribeToEvent = useCallback((eventId, onMessage) => {
    if (!eventId) return () => {};

    if (!listenersRef.current.has(eventId)) {
      listenersRef.current.set(eventId, new Set());
    }
    listenersRef.current.get(eventId).add(onMessage);

    // Setup WebSocket connection if not open or for this specific channel
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/events/${eventId}`;

    let socket;
    try {
      socket = new WebSocket(wsUrl);
      setStatus('CONNECTING');

      socket.onopen = () => {
        setStatus('CONNECTED');
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const callbacks = listenersRef.current.get(eventId);
          if (callbacks) {
            callbacks.forEach(cb => cb(payload));
          }
        } catch (e) {
          console.error('[WS] Parse error:', e);
        }
      };

      socket.onclose = () => {
        setStatus('DISCONNECTED');
      };

      socket.onerror = () => {
        setStatus('DISCONNECTED');
      };
    } catch (err) {
      console.warn('[WS] Connection failed:', err);
      setStatus('DISCONNECTED');
    }

    return () => {
      if (listenersRef.current.has(eventId)) {
        listenersRef.current.get(eventId).delete(onMessage);
        if (listenersRef.current.get(eventId).size === 0) {
          listenersRef.current.delete(eventId);
        }
      }
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, []);

  return (
    <RealtimeContext.Provider value={{ status, subscribeToEvent }}>
      {children}
    </RealtimeContext.Provider>
  );
};

export const useRealtime = () => useContext(RealtimeContext);
