import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useRealtime } from '../context/RealtimeContext';

const EventDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isOrganizer } = useAuth();
  const { subscribeToEvent } = useRealtime();

  const [event, setEvent] = useState(null);
  const [announcements, setAnnouncements] = useState([]);
  const [myRsvp, setMyRsvp] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  // Announcement posting form for Organizer
  const [newAnnTitle, setNewAnnTitle] = useState('');
  const [newAnnMessage, setNewAnnMessage] = useState('');
  const [isPostingAnn, setIsPostingAnn] = useState(false);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Fetch full event details
  const fetchEventData = useCallback(async () => {
    try {
      const [eventRes, annRes] = await Promise.all([
        api.get(`/events/${id}`),
        api.get(`/events/${id}/announcements`).catch(() => ({ data: { data: [] } }))
      ]);

      if (eventRes.data?.data) {
        setEvent(eventRes.data.data);
      }
      if (annRes.data?.data) {
        setAnnouncements(annRes.data.data);
      }

      // Check current user RSVP status if logged in
      if (user) {
        try {
          const myRsvpsRes = await api.get('/rsvps/me');
          const found = myRsvpsRes.data?.data?.find(r => r.event_id === id);
          if (found) setMyRsvp(found.status);
        } catch (e) {
          console.warn('Could not load user RSVP state:', e);
        }
      }
    } catch (err) {
      console.error('Failed to load event detail:', err);
    } finally {
      setLoading(false);
    }
  }, [id, user]);

  useEffect(() => {
    fetchEventData();
  }, [fetchEventData]);

  // Subscribe to real-time WebSocket channel for this event
  useEffect(() => {
    const unsubscribe = subscribeToEvent(id, (payload) => {
      if (payload.type === 'RSVP_UPDATE' && payload.data) {
        setEvent((prev) => prev ? {
          ...prev,
          going_count: payload.data.going_count,
          maybe_count: payload.data.maybe_count,
          not_going_count: payload.data.not_going_count,
          waitlist_count: payload.data.waitlist_count,
        } : null);
        showToast('Real-time RSVP count updated!');
      } else if (payload.type === 'ANNOUNCEMENT' && payload.data) {
        setAnnouncements((prev) => [payload.data, ...prev]);
        showToast(`New announcement: ${payload.data.title}`);
      } else if (payload.type === 'EVENT_STATUS_CHANGED') {
        setEvent((prev) => prev ? { ...prev, status: payload.status } : null);
      }
    });

    return () => unsubscribe();
  }, [id, subscribeToEvent]);

  // Handle RSVP action
  const handleRsvp = async (status) => {
    if (!user) {
      navigate('/login');
      return;
    }
    setActionLoading(true);
    try {
      const res = await api.post(`/events/${id}/rsvp`, { status });
      showToast(res.data.message || 'RSVP updated!');
      setMyRsvp(status);
      fetchEventData();
    } catch (err) {
      showToast(err.message || 'Failed to submit RSVP');
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Cancel RSVP
  const handleCancelRsvp = async () => {
    if (!user) return;
    setActionLoading(true);
    try {
      await api.delete(`/events/${id}/rsvp`);
      setMyRsvp(null);
      showToast('RSVP cancelled.');
      fetchEventData();
    } catch (err) {
      showToast(err.message || 'Failed to cancel RSVP');
    } finally {
      setActionLoading(false);
    }
  };

  // Organizer: Post new announcement
  const handleCreateAnnouncement = async (e) => {
    e.preventDefault();
    if (!newAnnTitle.trim() || !newAnnMessage.trim()) return;
    setIsPostingAnn(true);
    try {
      const res = await api.post(`/events/${id}/announcements`, {
        title: newAnnTitle,
        message: newAnnMessage
      });
      setAnnouncements(prev => [res.data.data, ...prev]);
      setNewAnnTitle('');
      setNewAnnMessage('');
      showToast('Announcement broadcasted to all attendees!');
    } catch (err) {
      showToast(err.message || 'Failed to post announcement');
    } finally {
      setIsPostingAnn(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
        Loading event details...
      </div>
    );
  }

  if (!event) {
    return (
      <div className="glass-card" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
        <h2>Event Not Found</h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
          This event may have been cancelled or deleted.
        </p>
      </div>
    );
  }

  const going = event.going_count ?? 0;
  const capacity = event.maximum_capacity || 100;
  const isFull = event.status === 'FULL' || going >= capacity;
  const spotsLeft = Math.max(0, capacity - going);
  const percentage = Math.min(Math.round((going / capacity) * 100), 100);

  return (
    <div>
      {/* Toast Notification */}
      {toastMessage && (
        <div className="toast">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <span className="live-dot" />
            <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{toastMessage}</span>
          </div>
        </div>
      )}

      {/* Hero Header Card */}
      <div className="glass-card" style={{ padding: '2.5rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', gap: '0.65rem', alignItems: 'center' }}>
            <span className="badge badge-category">{event.event_type}</span>
            {isFull ? (
              <span className="badge badge-full">Event Full</span>
            ) : (
              <span className="badge badge-published">Open Registration</span>
            )}
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Organized by Cloud Leader
          </span>
        </div>

        <h1 style={{ fontSize: 'clamp(2rem, 4vw, 2.75rem)', marginBottom: '1rem' }}>
          {event.event_name}
        </h1>

        {/* Date, Time, Venue Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '1.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            📅 <span>{event.event_date}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            ⏰ <span>{event.start_time?.substring(0, 5)} {event.end_time ? `- ${event.end_time.substring(0, 5)}` : ''}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            📍 <span>{event.is_online ? 'Virtual Webinar / Hub' : (event.venue || 'TBA')}</span>
          </div>
        </div>

        {event.is_online && event.online_link && (
          <div style={{ marginBottom: '1.5rem', padding: '0.75rem 1rem', background: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.3)', borderRadius: 'var(--radius-sm)', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
            <span>🔗 Stream URL:</span>
            <a href={event.online_link} target="_blank" rel="noreferrer" style={{ color: 'var(--cyan-accent)', textDecoration: 'underline' }}>
              {event.online_link}
            </a>
          </div>
        )}

        <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', lineHeight: 1.7, maxWidth: '850px' }}>
          {event.description || 'No detailed description available for this event.'}
        </p>
      </div>

      {/* Main Grid: RSVP Center & Announcements */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>
        
        {/* Left Column: Live RSVP Center */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '1.3rem' }}>Live RSVP Status</h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--emerald-accent)', fontWeight: 600 }}>● Instant Sync</span>
          </div>

          {/* Aggregate Metrics Bar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.875rem' }}>
            <span>Confirmed: {going} / {capacity}</span>
            <span style={{ fontWeight: 600, color: isFull ? 'var(--rose-accent)' : 'var(--emerald-accent)' }}>
              {isFull ? `${event.waitlist_count || 0} waiting` : `${spotsLeft} spots open`}
            </span>
          </div>

          <div className="capacity-track" style={{ height: '10px' }}>
            <div
              className="capacity-fill"
              style={{
                width: `${percentage}%`,
                background: isFull ? 'var(--rose-accent)' : 'var(--emerald-accent)'
              }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', margin: '1.5rem 0', textAlign: 'center' }}>
            <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '0.75rem', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--emerald-accent)' }}>{going}</span>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Going</p>
            </div>
            <div style={{ background: 'rgba(245, 158, 11, 0.1)', padding: '0.75rem', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--amber-accent)' }}>{event.maybe_count ?? 0}</span>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Maybe</p>
            </div>
            <div style={{ background: 'rgba(244, 63, 94, 0.1)', padding: '0.75rem', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--rose-accent)' }}>{event.not_going_count ?? 0}</span>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Can't Go</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1.25rem' }}>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem', fontWeight: 600 }}>
              {myRsvp ? `Your Status: ${myRsvp}` : 'Select your attendance:'}
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <button
                disabled={actionLoading}
                onClick={() => handleRsvp('GOING')}
                className={`btn ${myRsvp === 'GOING' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ width: '100%', justifyContent: 'flex-start', padding: '0.8rem 1.25rem' }}
              >
                <span>✅</span>
                <span>{isFull ? 'Join Waitlist (Event Full)' : "I'm Going"}</span>
              </button>

              <button
                disabled={actionLoading}
                onClick={() => handleRsvp('MAYBE')}
                className={`btn ${myRsvp === 'MAYBE' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ width: '100%', justifyContent: 'flex-start', padding: '0.8rem 1.25rem' }}
              >
                <span>🤔</span>
                <span>Maybe</span>
              </button>

              <button
                disabled={actionLoading}
                onClick={() => handleRsvp('NOT_GOING')}
                className={`btn ${myRsvp === 'NOT_GOING' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ width: '100%', justifyContent: 'flex-start', padding: '0.8rem 1.25rem' }}
              >
                <span>❌</span>
                <span>Can't Make It</span>
              </button>

              {myRsvp && (
                <button
                  disabled={actionLoading}
                  onClick={handleCancelRsvp}
                  className="btn btn-outline-danger"
                  style={{ width: '100%', marginTop: '0.5rem' }}
                >
                  Cancel My RSVP
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Live Announcements & Organizer Broadcasts */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.3rem', marginBottom: '1.25rem' }}>Event Announcements</h3>

          {/* Organizer Announcement Post Box */}
          {isOrganizer && (
            <form onSubmit={handleCreateAnnouncement} style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <h4 style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>Post Real-Time Update</h4>
              <input
                type="text"
                placeholder="Announcement Title"
                className="form-input"
                style={{ marginBottom: '0.5rem' }}
                value={newAnnTitle}
                onChange={(e) => setNewAnnTitle(e.target.value)}
                required
              />
              <textarea
                placeholder="Broadcast message to all registered attendees..."
                className="form-textarea"
                rows="2"
                style={{ marginBottom: '0.75rem' }}
                value={newAnnMessage}
                onChange={(e) => setNewAnnMessage(e.target.value)}
                required
              />
              <button disabled={isPostingAnn} type="submit" className="btn btn-primary btn-sm">
                {isPostingAnn ? 'Broadcasting...' : 'Broadcast Announcement'}
              </button>
            </form>
          )}

          {/* Announcements Feed */}
          {announcements.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', textAlign: 'center', padding: '2rem 0' }}>
              No announcements posted yet.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {announcements.map((ann) => (
                <div
                  key={ann.id}
                  style={{
                    padding: '1rem',
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                    <h4 style={{ fontSize: '0.95rem', color: '#c7d2fe' }}>{ann.title}</h4>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {new Date(ann.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                    {ann.message}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EventDetailPage;
