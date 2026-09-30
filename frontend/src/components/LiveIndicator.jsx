import React from 'react';
import { useRealtime } from '../context/RealtimeContext';

const LiveIndicator = () => {
  const { status } = useRealtime();

  const isConnected = status === 'CONNECTED';

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.45rem',
        padding: '0.3rem 0.65rem',
        borderRadius: '9999px',
        background: isConnected ? 'rgba(16, 185, 129, 0.12)' : 'rgba(245, 158, 11, 0.12)',
        border: `1px solid ${isConnected ? 'rgba(16, 185, 129, 0.25)' : 'rgba(245, 158, 11, 0.25)'}`,
        fontSize: '0.75rem',
        fontWeight: 600,
        color: isConnected ? 'var(--emerald-accent)' : 'var(--amber-accent)'
      }}
      title={isConnected ? 'Real-time WebSocket connection active' : 'Connecting to real-time events...'}
    >
      <span
        style={{
          width: '7px',
          height: '7px',
          borderRadius: '50%',
          backgroundColor: isConnected ? 'var(--emerald-accent)' : 'var(--amber-accent)',
          boxShadow: isConnected ? '0 0 8px var(--emerald-accent)' : 'none',
          animation: isConnected ? 'pulseLive 2s infinite' : 'none'
        }}
      />
      <span>{isConnected ? 'LIVE SYNC' : 'CONNECTING'}</span>
    </div>
  );
};

export default LiveIndicator;
