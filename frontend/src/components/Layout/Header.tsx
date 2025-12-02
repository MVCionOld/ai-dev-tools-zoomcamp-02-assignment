import React from 'react';
import { useNavigate } from 'react-router-dom';

interface HeaderProps {
  sessionName?: string;
  language?: string;
  onLanguageChange?: (language: string) => void;
  onRunCode?: () => void;
  isRunning?: boolean;
  shareUrl?: string;
  userCount?: number;
  supportedLanguages?: string[];
  currentUserRole?: 'creator' | 'participant';
}

export const Header: React.FC<HeaderProps> = ({
  sessionName = 'Untitled Session',
  language = 'python3.13',
  onLanguageChange,
  onRunCode,
  isRunning = false,
  shareUrl,
  userCount = 1,
  supportedLanguages = ['python3.13'],
  currentUserRole,
}) => {
  const navigate = useNavigate();

  const goHome = () => {
    navigate('/');
  };

  const copyShareUrl = async () => {
    if (shareUrl) {
      try {
        await navigator.clipboard.writeText(shareUrl);
        // Could add a toast notification here
        console.log('Share URL copied to clipboard');
      } catch (error) {
        console.error('Failed to copy URL:', error);
      }
    }
  };

  return (
    <header style={{ backgroundColor: 'white', borderBottom: '1px solid #e5e7eb', padding: '12px 24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {/* Left side - Session info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <button
            onClick={goHome}
            className="btn-secondary"
            style={{ fontSize: '14px', padding: '8px 12px' }}
            title="Go to home"
          >
            🏠 Home
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <h1 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {sessionName}
            </h1>
            {shareUrl && (
              <button
                onClick={copyShareUrl}
                className="btn-secondary"
                style={{ fontSize: '14px', padding: '4px 8px' }}
                title="Copy share link"
              >
                📋 Copy Link
              </button>
            )}
          </div>

          {/* Language selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label htmlFor="language-select" style={{ fontSize: '14px', fontWeight: '500', color: '#374151' }}>
              Language:
            </label>
            <select
              id="language-select"
              value={language}
              onChange={(e) => onLanguageChange?.(e.target.value)}
              className="input-field"
              style={{ fontSize: '14px', padding: '4px 8px', minWidth: '128px' }}
            >
              {supportedLanguages.map((lang) => (
                <option key={lang} value={lang}>
                  {lang === 'python3.13' ? 'Python 3.13' : lang}
                </option>
              ))}
            </select>
          </div>

          {/* Run button */}
          <button
            onClick={onRunCode}
            disabled={isRunning}
            className="btn-primary"
          >
            {isRunning ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid white',
                  borderTop: '2px solid transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                <span>Running...</span>
              </span>
            ) : (
              '▶️ Run'
            )}
          </button>
        </div>

        {/* Right side - User info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {currentUserRole && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '14px',
              color: '#374151',
              backgroundColor: currentUserRole === 'creator' ? '#dcfce7' : '#dbeafe',
              padding: '4px 8px',
              borderRadius: '6px',
              border: `1px solid ${currentUserRole === 'creator' ? '#16a34a' : '#2563eb'}`
            }}>
              <span>{currentUserRole === 'creator' ? '👑' : '👤'}</span>
              <span style={{ fontWeight: '500', textTransform: 'capitalize' }}>{currentUserRole}</span>
            </div>
          )}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: '#6b7280' }}>
            <span>👥</span>
            <span>{userCount} user{userCount !== 1 ? 's' : ''}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
