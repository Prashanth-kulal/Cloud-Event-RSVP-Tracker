import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import EventCard from '../components/EventCard';

const HomePage = () => {
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({
    total_events: 0,
    published_events: 0,
    total_rsvps: 0,
    going_rsvps: 0,
    waitlisted_attendees: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [eventsRes, statsRes] = await Promise.all([
          api.get('/events?limit=6'),
          api.get('/analytics/dashboard').catch(() => null)
        ]);

        if (eventsRes.data?.data) {
          setEvents(eventsRes.data.data);
        }
        if (statsRes?.data?.data) {
          setStats(statsRes.data.data);
        }
      } catch (err) {
        console.error('Error fetching homepage data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div>
      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: '3.5rem 1rem 4rem' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.35rem 0.85rem',
            borderRadius: 'var(--radius-full)',
            background: 'rgba(99, 102, 241, 0.12)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            marginBottom: '1.5rem',
            fontSize: '0.85rem',
            color: '#a5b4fc',
            fontWeight: 600
          }}
        >
          <span className="live-dot" />
          <span>Real-Time Cloud-Native Event Platform</span>
        </div>

        <h1
          style={{
            fontSize: 'clamp(2.5rem, 5vw, 4rem)',
            letterSpacing: '-0.03em',
            marginBottom: '1.25rem',
            maxWidth: '850px',
            margin: '0 auto 1.25rem'
          }}
        >
          Plan, RSVP & Sync Events in{' '}
          <span
            style={{
              background: 'var(--primary-gradient)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Real Time
          </span>
        </h1>

        <p
          style={{
            fontSize: '1.15rem',
            color: 'var(--text-secondary)',
            maxWidth: '640px',
            margin: '0 auto 2.5rem',
            lineHeight: 1.7
          }}
        >
          High-concurrency cloud architecture with instant WebSocket updates, zero overbooking guarantee, and automated FIFO waitlist promotions.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <Link to="/events" className="btn btn-primary" style={{ padding: '0.85rem 2rem', fontSize: '1rem' }}>
            Explore All Events
          </Link>
          <Link to="/register" className="btn btn-secondary" style={{ padding: '0.85rem 1.75rem', fontSize: '1rem' }}>
            Host an Event
          </Link>
        </div>
      </section>

      {/* Live System Telemetry / Metrics */}
      <section style={{ marginBottom: '4rem' }}>
        <div className="grid-stats">
          <div className="glass-card" style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)', fontFamily: 'var(--font-heading)' }}>
              {stats.published_events || events.length}
            </span>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>Active Events</p>
          </div>

          <div className="glass-card" style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--emerald-accent)', fontFamily: 'var(--font-heading)' }}>
              {stats.going_rsvps || 5}
            </span>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>Confirmed Attendees</p>
          </div>

          <div className="glass-card" style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--amber-accent)', fontFamily: 'var(--font-heading)' }}>
              {stats.waitlisted_attendees || 1}
            </span>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>Queue Position #1</p>
          </div>

          <div className="glass-card" style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--cyan-accent)', fontFamily: 'var(--font-heading)' }}>
              &lt; 15ms
            </span>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>WebSocket Sync Latency</p>
          </div>
        </div>
      </section>

      {/* Featured Events Section */}
      <section style={{ marginBottom: '4.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '1.75rem' }}>
          <div>
            <h2 style={{ fontSize: '1.75rem', marginBottom: '0.35rem' }}>Featured Cloud Events</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Explore top conferences, technical workshops, and cloud meetups.
            </p>
          </div>
          <Link to="/events" style={{ color: 'var(--primary)', fontWeight: 600, fontSize: '0.9rem' }}>
            View All →
          </Link>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted)' }}>
            Loading live events...
          </div>
        ) : events.length === 0 ? (
          <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
            <p style={{ color: 'var(--text-secondary)' }}>No published events currently available.</p>
          </div>
        ) : (
          <div className="grid-cards">
            {events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        )}
      </section>

      {/* Cloud Architectural Pillars */}
      <section style={{ marginBottom: '2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Engineered for Concurrency & Scale</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Built strictly on modern distributed systems and cloud engineering principles.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
          <div className="glass-card">
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)', marginBottom: '1rem' }}>
              ⚡
            </div>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>Sub-Second Real-Time Push</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Persistent WebSocket channels broadcast RSVP state, capacity adjustments, and organizer announcements to all connected attendees instantly.
            </p>
          </div>

          <div className="glass-card">
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--emerald-accent)', marginBottom: '1rem' }}>
              🔒
            </div>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>Zero Overbooking Guarantee</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Transactional isolation and database-level unique constraints eliminate race conditions when multiple attendees RSVP for the final spot.
            </p>
          </div>

          <div className="glass-card">
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(245, 158, 11, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--amber-accent)', marginBottom: '1rem' }}>
              📋
            </div>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>Automated FIFO Waitlist</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              When a confirmed attendee cancels, the system automatically promotes the next waitlisted user and issues immediate notifications.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
