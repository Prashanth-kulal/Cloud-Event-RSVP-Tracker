import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import NotificationBell from './NotificationBell';
import LiveIndicator from './LiveIndicator';

const Navbar = () => {
  const { user, logout, isOrganizer } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        background: 'rgba(9, 13, 22, 0.85)',
        backdropFilter: 'var(--glass-blur)',
        WebkitBackdropFilter: 'var(--glass-blur)',
        borderBottom: '1px solid var(--border-subtle)',
      }}
    >
      <div
        style={{
          maxWidth: 'var(--max-width)',
          margin: '0 auto',
          padding: '0.85rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '10px',
                background: 'var(--primary-gradient)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 15px rgba(99, 102, 241, 0.5)'
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2.5">
                <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"></path>
              </svg>
            </div>
            <div>
              <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '1.25rem', letterSpacing: '-0.02em' }}>
                Cloud<span style={{ color: 'var(--primary)' }}>RSVP</span>
              </span>
            </div>
          </Link>
          <LiveIndicator />
        </div>

        {/* Navigation Links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <Link
            to="/events"
            style={{
              fontSize: '0.925rem',
              fontWeight: 500,
              color: isActive('/events') ? 'var(--primary)' : 'var(--text-secondary)',
              transition: 'color 0.2s'
            }}
          >
            Explore Events
          </Link>

          {user && (
            <Link
              to="/my-rsvps"
              style={{
                fontSize: '0.925rem',
                fontWeight: 500,
                color: isActive('/my-rsvps') ? 'var(--primary)' : 'var(--text-secondary)',
                transition: 'color 0.2s'
              }}
            >
              My RSVPs
            </Link>
          )}

          {isOrganizer && (
            <Link
              to="/dashboard"
              style={{
                fontSize: '0.925rem',
                fontWeight: 500,
                color: isActive('/dashboard') ? 'var(--primary)' : 'var(--text-secondary)',
                transition: 'color 0.2s'
              }}
            >
              Dashboard
            </Link>
          )}
        </nav>

        {/* Auth / Action CTA */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {isOrganizer && (
            <Link to="/create-event" className="btn btn-primary btn-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Create Event
            </Link>
          )}

          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
              <NotificationBell />
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.35rem 0.65rem',
                  borderRadius: 'var(--radius-full)',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid var(--border-subtle)'
                }}
              >
                <span style={{ fontSize: '0.825rem', fontWeight: 600 }}>{user.name.split(' ')[0]}</span>
                <span
                  style={{
                    fontSize: '0.65rem',
                    padding: '0.15rem 0.4rem',
                    borderRadius: '4px',
                    background: isOrganizer ? 'rgba(99, 102, 241, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                    color: isOrganizer ? '#a5b4fc' : '#6ee7b7',
                    fontWeight: 700
                  }}
                >
                  {user.role}
                </span>
              </div>
              <button onClick={handleLogout} className="btn btn-secondary btn-sm" title="Sign Out">
                Logout
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <Link to="/login" className="btn btn-secondary btn-sm">
                Sign In
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm">
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
