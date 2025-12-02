import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface ProblemViewerProps {
  problemText: string;
  isCreator: boolean;
  onEdit?: () => void;
}

export const ProblemViewer: React.FC<ProblemViewerProps> = ({
  problemText,
  isCreator,
  onEdit,
}) => {
  if (!problemText || problemText.trim() === '') {
    return (
      <div style={{
        height: '100%',
        backgroundColor: 'white',
        border: '2px dashed #d1d5db',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center', color: '#6b7280', padding: '40px' }}>
          <div style={{ fontSize: '64px', marginBottom: '16px', opacity: 0.7 }}>🎯</div>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
            No problem statement
          </p>
          <p style={{ fontSize: '14px', marginBottom: '24px', color: '#6b7280', maxWidth: '300px', margin: '0 auto 24px' }}>
            {isCreator
              ? 'Add a coding problem for participants to solve'
              : 'Waiting for the session creator to add a problem statement'
            }
          </p>
          {isCreator && (
            <button
              onClick={onEdit}
              style={{
                backgroundColor: '#1a73e8',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                padding: '12px 24px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: '0 2px 4px rgba(26, 115, 232, 0.2)'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#1557b0';
                e.currentTarget.style.boxShadow = '0 4px 8px rgba(26, 115, 232, 0.3)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = '#1a73e8';
                e.currentTarget.style.boxShadow = '0 2px 4px rgba(26, 115, 232, 0.2)';
              }}
            >
              ✨ Add Problem Statement
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{
      height: '100%',
      backgroundColor: 'white',
      border: '2px solid #10b981',
      borderRadius: '8px',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px 20px',
        borderBottom: '1px solid #a7f3d0',
        backgroundColor: '#ecfdf5'
      }}>
        <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#065f46', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
          🎯 Problem Statement
        </h2>
        {isCreator && (
          <button
            onClick={onEdit}
            style={{
              backgroundColor: '#059669',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              padding: '8px 12px',
              cursor: 'pointer',
              fontWeight: '500',
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#047857'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#059669'}
          >
            ✏️ Edit
          </button>
        )}
      </div>

      {/* Content */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px',
        lineHeight: '1.6'
      }}>
        <div style={{
          maxWidth: 'none',
          fontSize: '15px',
          color: '#374151'
        }}>
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ className, children }) {
                const inline = !className?.includes('language-');
                const match = /language-(\w+)/.exec(className || '');
                const language = match ? match[1] : '';

                return !inline && language ? (
                  <SyntaxHighlighter
                    style={oneLight as any}
                    language={language}
                    PreTag="div"
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} style={{
                    backgroundColor: '#f1f5f9',
                    padding: '2px 4px',
                    borderRadius: '3px',
                    fontSize: '0.9em',
                    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace'
                  }}>
                    {children}
                  </code>
                );
              },
              table({ children }) {
                return (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      {children}
                    </table>
                  </div>
                );
              },
              th({ children }) {
                return (
                  <th className="px-3 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {children}
                  </th>
                );
              },
              td({ children }) {
                return (
                  <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-200">
                    {children}
                  </td>
                );
              },
            }}
          >
            {problemText}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};
