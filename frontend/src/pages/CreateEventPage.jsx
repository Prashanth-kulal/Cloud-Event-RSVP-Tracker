import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const EVENT_TYPES = ['WORKSHOP', 'CONFERENCE', 'SEMINAR', 'MEETUP', 'WEBINAR', 'TRAINING', 'NETWORKING', 'OTHER'];

const CreateEventPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    event_name: '',
    description: '',
    event_type: 'CONFERENCE',
    event_date: '',
    start_time: '09:00',
    end_time: '17:00',
    venue: '',
    online_link: '',
    maximum_capacity: 100,
    is_online: false,
    publish_now: true,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // 1. Create event
      const payload = {
        event_name: formData.event_name,
        description: formData.description,
        event_type: formData.event_type,
        event_date: formData.event_date,
        start_time: formData.start_time.length === 5 ? `${formData.start_time}:00` : formData.start_time,
        end_time: formData.end_time ? (formData.end_time.length === 5 ? `${formData.end_time}:00` : formData.end_time) : null,
        venue: formData.is_online ? 'Virtual' : formData.venue,
        online_link: formData.is_online ? formData.online_link : null,
        maximum_capacity: parseInt(formData.maximum_capacity, 10),
        is_online: formData.is_online,
      };

      const res = await api.post('/events', payload);
      const createdEvent = res.data?.data;

      // 2. Publish if selected
      if (formData.publish_now && createdEvent?.id) {
        await api.post(`/events/${createdEvent.id}/publish`);
      }

      navigate(`/events/${createdEvent.id}`);
    } catch (err) {
      setError(err.message || 'Failed to create event');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '720px', margin: '0 auto' }}>
      <div className="glass-card" style={{ padding: '2.5rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Create New Event</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          Publish an event with real-time RSVP tracking, live counters, and automated waitlist.
        </p>

        {error && (
          <div style={{ padding: '0.75rem 1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid var(--rose-accent)', borderRadius: 'var(--radius-sm)', color: '#fecdd3', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Event Name */}
          <div className="form-group">
            <label className="form-label">Event Name *</label>
            <input
              type="text"
              name="event_name"
              className="form-input"
              placeholder="e.g. Distributed Cloud & Kubernetes Summit 2026"
              value={formData.event_name}
              onChange={handleChange}
              required
            />
          </div>

          {/* Description */}
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              name="description"
              className="form-textarea"
              rows="4"
              placeholder="Detailed description of keynote speakers, sessions, agenda..."
              value={formData.description}
              onChange={handleChange}
            />
          </div>

          {/* Type & Capacity */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Event Type *</label>
              <select
                name="event_type"
                className="form-select"
                value={formData.event_type}
                onChange={handleChange}
              >
                {EVENT_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Maximum Capacity *</label>
              <input
                type="number"
                name="maximum_capacity"
                className="form-input"
                min="1"
                max="50000"
                value={formData.maximum_capacity}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          {/* Date & Times */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Event Date *</label>
              <input
                type="date"
                name="event_date"
                className="form-input"
                value={formData.event_date}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Start Time *</label>
              <input
                type="time"
                name="start_time"
                className="form-input"
                value={formData.start_time}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">End Time</label>
              <input
                type="time"
                name="end_time"
                className="form-input"
                value={formData.end_time}
                onChange={handleChange}
              />
            </div>
          </div>

          {/* Online Toggle */}
          <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', margin: '1rem 0' }}>
            <input
              type="checkbox"
              id="is_online"
              name="is_online"
              checked={formData.is_online}
              onChange={handleChange}
              style={{ width: '18px', height: '18px', accentColor: 'var(--primary)' }}
            />
            <label htmlFor="is_online" style={{ fontSize: '0.9rem', cursor: 'pointer' }}>
              This is a Virtual / Online Event
            </label>
          </div>

          {/* Location / Link */}
          {formData.is_online ? (
            <div className="form-group">
              <label className="form-label">Stream / Meeting URL</label>
              <input
                type="url"
                name="online_link"
                className="form-input"
                placeholder="https://zoom.us/j/... or Google Meet"
                value={formData.online_link}
                onChange={handleChange}
              />
            </div>
          ) : (
            <div className="form-group">
              <label className="form-label">Venue Location</label>
              <input
                type="text"
                name="venue"
                className="form-input"
                placeholder="e.g. Moscone Center, San Francisco, CA"
                value={formData.venue}
                onChange={handleChange}
              />
            </div>
          )}

          {/* Immediate Publish Option */}
          <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
            <input
              type="checkbox"
              id="publish_now"
              name="publish_now"
              checked={formData.publish_now}
              onChange={handleChange}
              style={{ width: '18px', height: '18px', accentColor: 'var(--primary)' }}
            />
            <label htmlFor="publish_now" style={{ fontSize: '0.9rem', cursor: 'pointer' }}>
              Publish immediately (visible to all attendees)
            </label>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/events')}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ padding: '0.75rem 2rem' }}
            >
              {loading ? 'Creating Event...' : 'Create & Launch Event'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateEventPage;
