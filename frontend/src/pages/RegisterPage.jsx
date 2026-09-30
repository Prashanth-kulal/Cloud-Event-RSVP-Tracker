import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('ATTENDEE');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await register(name, email, password, role);
      navigate(role === 'ORGANIZER' ? '/dashboard' : '/events');
    } catch (err) {
      setError(err.message || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '460px', margin: '2rem auto' }}>
      <div className="glass-card" style={{ padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '1.85rem', marginBottom: '0.4rem' }}>Create Account</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Join the real-time event platform as an attendee or organizer.
          </p>
        </div>

        {error && (
          <div
            style={{
              padding: '0.75rem 1rem',
              background: 'rgba(244, 63, 94, 0.15)',
              border: '1px solid var(--rose-accent)',
              borderRadius: 'var(--radius-sm)',
              color: '#fecdd3',
              marginBottom: '1.5rem',
              fontSize: '0.875rem'
            }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="Sarah Connor"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              className="form-input"
              placeholder="you@domain.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password (min 8 characters)</label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              required
            />
          </div>

          {/* Role Selection */}
          <div className="form-group">
            <label className="form-label">Account Role</label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div
                onClick={() => setRole('ATTENDEE')}
                style={{
                  padding: '0.85rem',
                  borderRadius: 'var(--radius-sm)',
                  border: `2px solid ${role === 'ATTENDEE' ? 'var(--primary)' : 'var(--border-subtle)'}`,
                  background: role === 'ATTENDEE' ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                  cursor: 'pointer',
                  textAlign: 'center',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{ fontSize: '1.25rem', marginBottom: '0.2rem' }}>🎟️</div>
                <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>Attendee</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>RSVP & join events</div>
              </div>

              <div
                onClick={() => setRole('ORGANIZER')}
                style={{
                  padding: '0.85rem',
                  borderRadius: 'var(--radius-sm)',
                  border: `2px solid ${role === 'ORGANIZER' ? 'var(--primary)' : 'var(--border-subtle)'}`,
                  background: role === 'ORGANIZER' ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                  cursor: 'pointer',
                  textAlign: 'center',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{ fontSize: '1.25rem', marginBottom: '0.2rem' }}>👑</div>
                <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>Organizer</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Host & manage events</div>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.75rem', marginTop: '0.75rem' }}
          >
            {loading ? 'Creating Account...' : 'Get Started'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.75rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--primary)', fontWeight: 600 }}>
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
