import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const MyRsvpsPage = () => {
  const [rsvps, setRsvps] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMyRsvps = async () => {
    try {
      const res = await api.get('/rsvps/me');
      if (res.data?.data) {
        setRsvps(res.data.data);
      }
    } catch (err) {
      console.error('Failed to load my RSVPs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMyRsvps();
  }, []);

  const handleCancelRsvp = async (eventId) => {
    if (!window.confirm('Cancel this RSVP?')) return;
    try {
      await api.delete(`/events/${eventId}/rsvp`);
      fetchMyRsvps();
    } catch (err) {
      alert(err.message || 'Failed to cancel RSVP');
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'GOING':
        return <span className="badge badge-published">Going</span>;
      case 'MAYBE':
        return <span className="badge badge-draft">Maybe</span>;
      default:
        return <span className="badge badge-full">Not Going</span>;
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.25rem', marginBottom: '0.4rem' }}>My RSVPs</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Manage your upcoming event registrations, waitlist status, and invitations.
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>
          Loading your registrations...
        </div>
      ) : rsvps.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3.5rem 1rem' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>No registrations found</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            You haven't RSVP'd to any events yet.
          </p>
          <Link to="/events" className="btn btn-primary">
            Browse Upcoming Events
          </Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {rsvps.map((r) => (
            <div
              key={r.id || r.event_id}
              className="glass-card"
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '1rem',
                padding: '1.25rem 1.75rem'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.4rem' }}>
                  {getStatusBadge(r.status)}
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Responded: {new Date(r.responded_at || r.updated_at).toLocaleDateString()}
                  </span>
                </div>
                <h3 style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>
                  <Link to={`/events/${r.event_id}`} style={{ color: 'inherit' }}>
                    {r.event_name || 'Event Registration'}
                  </Link>
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  ID: {r.event_id}
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Link to={`/events/${r.event_id}`} className="btn btn-secondary btn-sm">
                  View Event
                </Link>
                <button
                  onClick={() => handleCancelRsvp(r.event_id)}
                  className="btn btn-outline-danger btn-sm"
                >
                  Cancel RSVP
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyRsvpsPage;
