import React, { useState, useRef, useEffect } from 'react';
import { useNotifications } from '../context/NotificationContext';

const NotificationBell = () => {
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications();
  const [isOpen, setIsOpen] = useState(false);
  const panelRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div style={{ position: 'relative' }} ref={panelRef}>
      <button
        className="btn btn-secondary"
        style={{ padding: '0.45rem 0.65rem', borderRadius: '50%', position: 'relative' }}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="View notifications"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
        </svg>
        {unreadCount > 0 && (
          <span
            style={{
              position: 'absolute',
              top: '-4px',
              right: '-4px',
              background: 'var(--rose-accent)',
              color: '#ffffff',
              fontSize: '0.65rem',
              fontWeight: 800,
              width: '18px',
              height: '18px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid var(--bg-surface)'
            }}
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 10px)',
            right: 0,
            width: '320px',
            maxHeight: '400px',
            overflowY: 'auto',
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-glow)',
            backdropFilter: 'var(--glass-blur)',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-hover)',
            zIndex: 100,
            padding: '1rem'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <h4 style={{ fontSize: '0.95rem' }}>Notifications</h4>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                style={{ background: 'none', border: 'none', color: 'var(--primary)', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600 }}
              >
                Mark all read
              </button>
            )}
          </div>

          {notifications.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '1rem 0' }}>
              No notifications yet.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {notifications.map((n) => (
                <div
                  key={n.id}
                  onClick={() => !n.read && markAsRead(n.id)}
                  style={{
                    padding: '0.65rem',
                    borderRadius: 'var(--radius-sm)',
                    background: n.read ? 'rgba(255, 255, 255, 0.02)' : 'rgba(99, 102, 241, 0.1)',
                    border: `1px solid ${n.read ? 'transparent' : 'rgba(99, 102, 241, 0.2)'}`,
                    cursor: n.read ? 'default' : 'pointer',
                    fontSize: '0.825rem',
                    transition: 'background 0.2s'
                  }}
                >
                  <p style={{ color: n.read ? 'var(--text-secondary)' : 'var(--text-primary)', marginBottom: '0.25rem' }}>
                    {n.message}
                  </p>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
