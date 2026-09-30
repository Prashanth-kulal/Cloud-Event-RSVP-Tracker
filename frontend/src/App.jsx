import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { RealtimeProvider } from './context/RealtimeContext';
import { NotificationProvider } from './context/NotificationContext';

import Navbar from './components/Navbar';
import Footer from './components/Footer';

import HomePage from './pages/HomePage';
import EventsPage from './pages/EventsPage';
import EventDetailPage from './pages/EventDetailPage';
import CreateEventPage from './pages/CreateEventPage';
import DashboardPage from './pages/DashboardPage';
import MyRsvpsPage from './pages/MyRsvpsPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Protected Route for authenticated users
const ProtectedRoute = ({ children, organizerOnly = false }) => {
  const { user, loading, isOrganizer } = useAuth();

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
        Authenticating session...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (organizerOnly && !isOrganizer) {
    return <Navigate to="/" replace />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <RealtimeProvider>
          <NotificationProvider>
            <div className="app-container">
              <Navbar />
              <main className="main-content">
                <Routes>
                  {/* Public Routes */}
                  <Route path="/" element={<HomePage />} />
                  <Route path="/events" element={<EventsPage />} />
                  <Route path="/events/:id" element={<EventDetailPage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />

                  {/* Protected Routes */}
                  <Route
                    path="/my-rsvps"
                    element={
                      <ProtectedRoute>
                        <MyRsvpsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/create-event"
                    element={
                      <ProtectedRoute organizerOnly>
                        <CreateEventPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/dashboard"
                    element={
                      <ProtectedRoute organizerOnly>
                        <DashboardPage />
                      </ProtectedRoute>
                    }
                  />

                  {/* Fallback */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </main>
              <Footer />
            </div>
          </NotificationProvider>
        </RealtimeProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
