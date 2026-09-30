import React, { useState, useEffect } from 'react';
import api from '../services/api';
import EventCard from '../components/EventCard';

const CATEGORIES = ['ALL', 'CONFERENCE', 'WORKSHOP', 'MEETUP', 'WEBINAR', 'SEMINAR'];

const EventsPage = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  useEffect(() => {
    const fetchEvents = async () => {
      setLoading(true);
      try {
        let url = '/events?';
        const params = new URLSearchParams();
        if (selectedCategory !== 'ALL') {
          params.append('event_type', selectedCategory);
        }
        if (statusFilter !== 'ALL') {
          params.append('status', statusFilter);
        }
        if (search.trim()) {
          params.append('search', search.trim());
        }

        const res = await api.get(`/events?${params.toString()}`);
        if (res.data?.data) {
          setEvents(res.data.data);
        }
      } catch (err) {
        console.error('Failed to load events:', err);
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(fetchEvents, 250);
    return () => clearTimeout(timer);
  }, [search, selectedCategory, statusFilter]);

  return (
    <div>
      {/* Title & Filters */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.25rem', marginBottom: '0.5rem' }}>Explore Events</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.75rem' }}>
          Discover upcoming conferences, hands-on workshops, and community tech meetups.
        </p>

        {/* Search & Filter Bar */}
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: 1, minWidth: '260px' }}>
            <input
              type="text"
              className="form-input"
              placeholder="Search events by title or keyword..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div style={{ width: '180px' }}>
            <select
              className="form-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="PUBLISHED">Open RSVP</option>
              <option value="FULL">Event Full</option>
            </select>
          </div>
        </div>

        {/* Category Pills */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '1rem' }}>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={selectedCategory === cat ? 'btn btn-primary btn-sm' : 'btn btn-secondary btn-sm'}
              style={{ borderRadius: 'var(--radius-full)' }}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Events Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>
          Loading events catalog...
        </div>
      ) : events.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3.5rem 1rem' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>No events found</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Try adjusting your search query or filters.
          </p>
        </div>
      ) : (
        <div className="grid-cards">
          {events.map((event) => (
            <EventCard key={event.id} event={event} />
          ))}
        </div>
      )}
    </div>
  );
};

export default EventsPage;
