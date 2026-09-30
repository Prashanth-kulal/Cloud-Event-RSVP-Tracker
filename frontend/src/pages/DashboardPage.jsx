import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const DashboardPage = () => {
  const { user } = useAuth();
  const [events, setEvents] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [waitlistModalEvent, setWaitlistModalEvent] = useState(null);
  const [waitlistEntries, setWaitlistEntries] = useState([]);
  const [waitlistLoading, setWaitlistLoading] = useState(false);

  const fetchDashboardData = useCallback(async () => {
    try {
      const [eventsRes, summaryRes] = await Promise.all([
        api.get('/events/organizer/my-events').catch(() => ({ data: { data: [] } })),
        api.get('/analytics/dashboard').catch(() => ({ data: { data: null } }))
      ]);

      if (eventsRes.data?.data) {
        setEvents(eventsRes.data.data);
      }
      if (summaryRes.data?.data) {
        setSummary(summaryRes.data.data);
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Handle Publish Event
  const handlePublish = async (eventId) => {
    try {
      await api.post(`/events/${eventId}/publish`);
      fetchDashboardData();
    } catch (err) {
      alert(err.message || 'Failed to publish event');
    }
  };

  // Handle Cancel Event
  const handleCancel = async (eventId) => {
    if (!window.confirm('Are you sure you want to cancel this event? Attendees will be notified.')) return;
    try {
      await api.post(`/events/${eventId}/cancel`);
      fetchDashboardData();
    } catch (err) {
      alert(err.message || 'Failed to cancel event');
    }
  };

  // Open waitlist modal
  const openWaitlistModal = async (event) => {
    setWaitlistModalEvent(event);
    setWaitlistLoading(true);
    try {
      const res = await api.get(`/events/${event.id}/waitlist`);
      setWaitlistEntries(res.data?.data || []);
    } catch (err) {
      console.error('Failed to load waitlist:', err);
      setWaitlistEntries([]);
    } finally {
      setWaitlistLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
        Loading organizer dashboard...
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '2.5rem' }}>
        <div>
          <h1 style={{ fontSize: '2.25rem', marginBottom: '0.4rem' }}>Organizer Dashboard</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            Real-time management, attendee capacity, and waitlist automation.
          </p>
        </div>
        <Link to="/create-event" className="btn btn-primary">
          + Create New Event
        </Link>
      </div>

      {/* Metric Cards */}
      <div className="grid-stats" style={{ marginBottom: '2.5rem' }}>
        <div className="glass-card">
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Total Hosted Events</p>
          <p style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)', marginTop: '0.25rem' }}>
            {events.length}
          </p>
        </div>

        <div className="glass-card">
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Confirmed RSVPs</p>
          <p style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--emerald-accent)', marginTop: '0.25rem' }}>
            {summary?.going_rsvps ?? events.reduce((acc, e) => acc + (e.going_count || 0), 0)}
          </p>
        </div>

        <div className="glass-card">
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Waitlist Queue</p>
          <p style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--amber-accent)', marginTop: '0.25rem' }}>
            {summary?.waitlisted_attendees ?? events.reduce((acc, e) => acc + (e.waitlist_count || 0), 0)}
          </p>
        </div>

        <div className="glass-card">
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Avg Attendance Rate</p>
          <p style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--cyan-accent)', marginTop: '0.25rem' }}>
            88.5%
          </p>
        </div>
      </div>

      {/* Events Table Card */}
      <div className="glass-card" style={{ padding: '1.5rem', overflowX: 'auto' }}>
        <h2 style={{ fontSize: '1.4rem', marginBottom: '1.25rem' }}>Your Hosted Events</h2>

        {events.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
            You haven't created any events yet.{' '}
            <Link to="/create-event" style={{ color: 'var(--primary)', fontWeight: 600 }}>
              Create your first event
            </Link>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Event</th>
                <th style={{ padding: '0.75rem 1rem' }}>Date</th>
                <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                <th style={{ padding: '0.75rem 1rem' }}>Capacity / Going</th>
                <th style={{ padding: '0.75rem 1rem' }}>Waitlist</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => {
                const going = e.going_count || 0;
                const cap = e.maximum_capacity || 100;
                const pct = Math.min(Math.round((going / cap) * 100), 100);

                return (
                  <tr key={e.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '1rem', fontWeight: 600 }}>
                      <Link to={`/events/${e.id}`} style={{ color: 'var(--text-primary)' }}>
                        {e.event_name}
                      </Link>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                        {e.event_type} • {e.is_online ? 'Virtual' : (e.venue || 'Venue TBD')}
                      </div>
                    </td>

                    <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>
                      {e.event_date}
                    </td>

                    <td style={{ padding: '1rem' }}>
                      <span className={`badge badge-${e.status.toLowerCase()}`}>
                        {e.status}
                      </span>
                    </td>

                    <td style={{ padding: '1rem', minWidth: '150px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.2rem' }}>
                        <span>{going} / {cap}</span>
                        <span>{pct}%</span>
                      </div>
                      <div className="capacity-track" style={{ height: '6px' }}>
                        <div className="capacity-fill" style={{ width: `${pct}%`, background: pct >= 100 ? 'var(--rose-accent)' : 'var(--emerald-accent)' }} />
                      </div>
                    </td>

                    <td style={{ padding: '1rem' }}>
                      {e.waitlist_count > 0 ? (
                        <button
                          onClick={() => openWaitlistModal(e)}
                          className="btn btn-secondary btn-sm"
                          style={{ color: 'var(--amber-accent)' }}
                        >
                          {e.waitlist_count} waiting →
                        </button>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>None</span>
                      )}
                    </td>

                    <td style={{ padding: '1rem', textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                        {e.status === 'DRAFT' && (
                          <button
                            onClick={() => handlePublish(e.id)}
                            className="btn btn-primary btn-sm"
                          >
                            Publish
                          </button>
                        )}
                        {e.status === 'PUBLISHED' && (
                          <button
                            onClick={() => handleCancel(e.id)}
                            className="btn btn-outline-danger btn-sm"
                          >
                            Cancel
                          </button>
                        )}
                        <Link to={`/events/${e.id}`} className="btn btn-secondary btn-sm">
                          View
                        </Link>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Waitlist Inspect Modal */}
      {waitlistModalEvent && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'var(--glass-blur)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1rem'
          }}
        >
          <div className="glass-card" style={{ maxWidth: '520px', width: '100%', padding: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.25rem' }}>Waitlist Queue</h3>
              <button
                onClick={() => setWaitlistModalEvent(null)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '1.25rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.25rem' }}>
              Event: <strong style={{ color: 'var(--text-primary)' }}>{waitlistModalEvent.event_name}</strong>
            </p>

            {waitlistLoading ? (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '1.5rem 0' }}>Loading waitlist entries...</p>
            ) : waitlistEntries.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '1.5rem 0' }}>No attendees currently on the waitlist.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '300px', overflowY: 'auto' }}>
                {waitlistEntries.map((w) => (
                  <div
                    key={w.id}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '0.75rem 1rem',
                      background: 'rgba(255, 255, 255, 0.03)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--border-subtle)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <span
                        style={{
                          width: '26px',
                          height: '26px',
                          borderRadius: '50%',
                          background: 'rgba(245, 158, 11, 0.2)',
                          color: 'var(--amber-accent)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '0.8rem',
                          fontWeight: 700
                        }}
                      >
                        #{w.position}
                      </span>
                      <div>
                        <p style={{ fontSize: '0.9rem', fontWeight: 600 }}>{w.user_name || 'Attendee'}</p>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{w.user_email || 'Registered User'}</p>
                      </div>
                    </div>
                    <span className="badge badge-draft" style={{ fontSize: '0.7rem' }}>
                      {w.status}
                    </span>
                  </div>
                ))}
              </div>
            )}

            <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
              <button onClick={() => setWaitlistModalEvent(null)} className="btn btn-secondary btn-sm">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
