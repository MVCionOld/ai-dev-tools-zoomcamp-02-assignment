import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCreateSession, useSessions, useDeleteSession, useExecutors } from '../../hooks/useApi';
import type { CreateSessionRequest } from '../../types/api';

export const SessionList: React.FC = () => {
  const navigate = useNavigate();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newSession, setNewSession] = useState<CreateSessionRequest>({
    name: '',
    language: 'python3.13',
  });

  const { data: sessions, isLoading } = useSessions();
  const { data: executors } = useExecutors();
  const createSessionMutation = useCreateSession();
  const deleteSessionMutation = useDeleteSession();

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSession.name.trim()) return;

    try {
      const session = await createSessionMutation.mutateAsync(newSession);
      navigate(`/session/${session.id}`);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    if (confirm('Are you sure you want to delete this session?')) {
      try {
        await deleteSessionMutation.mutateAsync(sessionId);
      } catch (error) {
        console.error('Failed to delete session:', error);
      }
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-gray-300 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading sessions...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 16px' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '32px' }}>
          <div>
            <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#111827', margin: '0 0 8px 0' }}>
              🎯 Coding Sessions
            </h1>
            <p style={{ color: '#6b7280', fontSize: '16px', margin: 0 }}>
              Create and manage your coding interview sessions
            </p>
          </div>
          {sessions && sessions.length > 0 && (
            <button
              onClick={() => setShowCreateForm(true)}
              className="btn-primary"
              style={{ fontSize: '16px', padding: '12px 24px' }}
            >
              ➕ New Session
            </button>
          )}
        </div>

        {/* Create Session Form */}
        {showCreateForm && (
          <div className="card" style={{ padding: '24px', marginBottom: '32px', border: '2px solid #e5e7eb', borderRadius: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', margin: 0 }}>
                ✨ Create New Session
              </h2>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer' }}
                title="Close"
              >
                ✖️
              </button>
            </div>
            <form onSubmit={handleCreateSession} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label htmlFor="session-name" style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '4px' }}>
                  Session Name
                </label>
                <input
                  id="session-name"
                  type="text"
                  value={newSession.name}
                  onChange={(e) => setNewSession({ ...newSession, name: e.target.value })}
                  placeholder="e.g., Two Sum Problem Interview"
                  className="input-field"
                  style={{ fontSize: '16px' }}
                  required
                />
              </div>
              <div>
                <label htmlFor="language" style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '4px' }}>
                  Programming Language
                </label>
                <select
                  id="language"
                  value={newSession.language}
                  onChange={(e) => setNewSession({ ...newSession, language: e.target.value })}
                  className="input-field"
                  style={{ fontSize: '16px' }}
                >
                  {(executors || []).map((executor) => (
                    <option key={executor.language} value={executor.language}>
                      {executor.display_name}
                    </option>
                  ))}
                </select>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <button
                  type="submit"
                  disabled={createSessionMutation.isPending || !newSession.name.trim()}
                  className="btn-primary"
                  style={{ fontSize: '16px', padding: '12px 24px' }}
                >
                  {createSessionMutation.isPending ? '🔄 Creating...' : '🚀 Create Session'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="btn-secondary"
                  style={{ fontSize: '16px', padding: '12px 24px' }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Sessions List */}
        {sessions && sessions.length > 0 ? (
          <div style={{ display: 'grid', gap: '16px' }}>
            {sessions.map((session) => (
              <div
                key={session.id}
                className="card"
                style={{
                  padding: '24px',
                  transition: 'box-shadow 0.2s ease',
                  cursor: 'pointer',
                  border: '1px solid #e5e7eb'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '8px' }}>
                      <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', margin: 0 }}>
                        📝 {session.name}
                      </h3>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        padding: '4px 12px',
                        borderRadius: '20px',
                        fontSize: '12px',
                        fontWeight: '500',
                        backgroundColor: '#dbeafe',
                        color: '#1e40af'
                      }}>
                        {session.language === 'python3.13' ? 'Python 3.13' : session.language}
                      </span>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        padding: '4px 12px',
                        borderRadius: '20px',
                        fontSize: '12px',
                        fontWeight: '500',
                        backgroundColor: session.is_active ? '#dcfce7' : '#f3f4f6',
                        color: session.is_active ? '#166534' : '#374151'
                      }}>
                        {session.is_active ? '🟢 Active' : '⚪ Inactive'}
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '24px', fontSize: '14px', color: '#6b7280' }}>
                      <span>📅 Created: {formatDate(session.created_at)}</span>
                      <span>⏰ Expires: {formatDate(session.expires_at)}</span>
                      <span>👥 {session.users?.length || 0} users</span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <button
                      onClick={() => navigate(`/session/${session.id}`)}
                      className="btn-primary"
                      style={{ fontSize: '14px', padding: '8px 16px' }}
                    >
                      🚀 Join Session
                    </button>
                    <button
                      onClick={() => handleDeleteSession(session.id)}
                      disabled={deleteSessionMutation.isPending}
                      className="btn-secondary"
                      style={{
                        fontSize: '14px',
                        padding: '8px 12px',
                        color: '#dc2626',
                        opacity: deleteSessionMutation.isPending ? 0.5 : 1
                      }}
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '80px 24px' }}>
            <div style={{ fontSize: '80px', marginBottom: '24px', opacity: 0.8 }}>💻</div>
            <h3 style={{ fontSize: '24px', fontWeight: '600', color: '#111827', marginBottom: '12px' }}>
              Ready to start coding?
            </h3>
            <p style={{ color: '#6b7280', fontSize: '16px', marginBottom: '32px', maxWidth: '400px', margin: '0 auto 32px' }}>
              Create your first coding interview session and collaborate with others in real-time
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
              <button
                onClick={() => setShowCreateForm(true)}
                className="btn-primary"
                style={{
                  fontSize: '18px',
                  padding: '16px 32px',
                  borderRadius: '12px',
                  boxShadow: '0 4px 12px rgba(26, 115, 232, 0.3)'
                }}
              >
                ✨ Create Your First Session
              </button>
              <div style={{ display: 'flex', alignItems: 'center', gap: '24px', fontSize: '14px', color: '#9ca3af' }}>
                <span>🔥 Real-time collaboration</span>
                <span>⚡ Instant code execution</span>
                <span>📝 Problem statement editor</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
