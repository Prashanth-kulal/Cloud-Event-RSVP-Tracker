import React from 'react';

const Footer = () => {
  return (
    <footer
      style={{
        borderTop: '1px solid var(--border-subtle)',
        background: 'rgba(10, 15, 26, 0.95)',
        padding: '2.5rem 1.5rem',
        marginTop: 'auto',
      }}
    >
      <div
        style={{
          maxWidth: 'var(--max-width)',
          margin: '0 auto',
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '1.5rem',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
            <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '1.1rem' }}>
              Cloud<span style={{ color: 'var(--primary)' }}>RSVP</span>
            </span>
            <span className="badge badge-published" style={{ fontSize: '0.65rem' }}>Cloud-Native v1.0</span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.825rem', maxWidth: '420px' }}>
            High-concurrency, real-time distributed event planning & RSVP tracker powered by FastAPI, SQLite/PostgreSQL, WebSockets, and Cloud Infrastructure.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '2rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          <div>
            <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>Architecture</p>
            <p style={{ color: 'var(--text-muted)' }}>FastAPI + WebSocket ASGI</p>
            <p style={{ color: 'var(--text-muted)' }}>Async SQLAlchemy & ACID locks</p>
          </div>
          <div>
            <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>Real-Time Sync</p>
            <p style={{ color: 'var(--text-muted)' }}>FIFO Waitlist Promotion</p>
            <p style={{ color: 'var(--text-muted)' }}>Channel-based pub/sub broadcast</p>
          </div>
        </div>
      </div>
      <div
        style={{
          maxWidth: 'var(--max-width)',
          margin: '1.5rem auto 0',
          paddingTop: '1rem',
          borderTop: '1px solid rgba(255, 255, 255, 0.04)',
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
        }}
      >
        <span>© 2026 Real-Time Cloud-Based Event Planning & RSVP Tracker. All rights reserved.</span>
        <span>Zero Overbooking Guarantee • Concurrency Safe</span>
      </div>
    </footer>
  );
};

export default Footer;
