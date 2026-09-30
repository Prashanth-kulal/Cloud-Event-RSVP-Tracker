import React from 'react';
import { Link } from 'react-router-dom';

const EventCard = ({ event }) => {
  const going = event.going_count ?? 0;
  const capacity = event.maximum_capacity || 100;
  const isFull = event.status === 'FULL' || going >= capacity;
  const percentage = Math.min(Math.round((going / capacity) * 100), 100);
  const spotsLeft = Math.max(0, capacity - going);

  const getStatusBadge = () => {
    if (event.status === 'FULL' || isFull) {
      return <span className="badge badge-full">Event Full</span>;
    }
    if (event.status === 'DRAFT') {
      return <span className="badge badge-draft">Draft</span>;
    }
    return <span className="badge badge-published">Open RSVP</span>;
  };

  const getProgressColor = () => {
    if (percentage >= 90) return 'var(--rose-accent)';
    if (percentage >= 70) return 'var(--amber-accent)';
    return 'var(--emerald-accent)';
  };

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header Tags */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
        <span className="badge badge-category">{event.event_type}</span>
        {getStatusBadge()}
      </div>

      {/* Title */}
      <h3 style={{ fontSize: '1.2rem', marginBottom: '0.65rem' }}>
        <Link to={`/events/${event.id}`} style={{ color: 'inherit' }}>
          {event.event_name}
        </Link>
      </h3>

      {/* Description Snippet */}
      <p
        style={{
          color: 'var(--text-secondary)',
          fontSize: '0.875rem',
          marginBottom: '1rem',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          flex: 1
        }}
      >
        {event.description || 'No description provided.'}
      </p>

      {/* Meta Information: Date, Time, Venue */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.825rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          <span>{event.event_date} • {event.start_time?.substring(0, 5)}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
          <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {event.is_online ? '🌐 Online Stream' : (event.venue || 'TBD')}
          </span>
        </div>
      </div>

      {/* Capacity Utilization Progress Bar */}
      <div style={{ marginTop: 'auto', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.775rem', color: 'var(--text-secondary)' }}>
          <span>Capacity: {going} / {capacity}</span>
          <span style={{ fontWeight: 600, color: getProgressColor() }}>
            {isFull ? (event.waitlist_count > 0 ? `${event.waitlist_count} on waitlist` : 'Full') : `${spotsLeft} spots left`}
          </span>
        </div>
        <div className="capacity-track">
          <div
            className="capacity-fill"
            style={{
              width: `${percentage}%`,
              background: getProgressColor(),
            }}
          />
        </div>
      </div>

      {/* Action Button */}
      <div style={{ marginTop: '1rem' }}>
        <Link
          to={`/events/${event.id}`}
          className="btn btn-secondary"
          style={{ width: '100%', fontSize: '0.875rem', padding: '0.55rem' }}
        >
          View Details & RSVP
        </Link>
      </div>
    </div>
  );
};

export default EventCard;
