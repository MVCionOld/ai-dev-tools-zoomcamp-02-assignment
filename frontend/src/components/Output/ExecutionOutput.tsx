import React from 'react';
import type { ExecutionResult } from '../../types/api';

interface ExecutionOutputProps {
  result?: ExecutionResult;
  isRunning?: boolean;
  error?: string;
}

export const ExecutionOutput: React.FC<ExecutionOutputProps> = ({
  result,
  isRunning = false,
  error,
}) => {
  if (error) {
    return (
      <div style={{
        height: '100%',
        backgroundColor: 'white',
        border: '2px solid #f87171',
        borderRadius: '8px',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        <div style={{
          padding: '12px 16px',
          backgroundColor: '#fef2f2',
          borderBottom: '1px solid #fecaca',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <div style={{
            width: '16px',
            height: '16px',
            borderRadius: '50%',
            backgroundColor: '#ef4444',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '10px',
            color: 'white',
            fontWeight: 'bold'
          }}>!</div>
          <h3 style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#dc2626',
            margin: 0
          }}>Execution Error</h3>
        </div>
        <div style={{
          flex: 1,
          padding: '16px',
          overflow: 'auto'
        }}>
          <div style={{
            backgroundColor: '#fee2e2',
            border: '1px solid #fca5a5',
            borderRadius: '6px',
            padding: '12px'
          }}>
            <pre style={{
              fontSize: '13px',
              color: '#991b1b',
              whiteSpace: 'pre-wrap',
              fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace',
              margin: 0
            }}>
              {error}
            </pre>
          </div>
        </div>
      </div>
    );
  }

  if (isRunning) {
    return (
      <div style={{
        height: '100%',
        backgroundColor: 'white',
        border: '2px solid #3b82f6',
        borderRadius: '8px',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        <div style={{
          padding: '12px 16px',
          backgroundColor: '#dbeafe',
          borderBottom: '1px solid #93c5fd',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <div style={{
            width: '14px',
            height: '14px',
            border: '2px solid #2563eb',
            borderTopColor: 'transparent',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }}></div>
          <h3 style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#1d4ed8',
            margin: 0
          }}>Running Code...</h3>
        </div>
        <div style={{
          flex: 1,
          padding: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#6b7280'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              width: '32px',
              height: '32px',
              border: '3px solid #e5e7eb',
              borderTopColor: '#3b82f6',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 8px'
            }}></div>
            <p style={{
              fontSize: '14px',
              margin: 0,
              color: '#374151'
            }}>Executing your code...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div style={{
        height: '100%',
        backgroundColor: 'white',
        border: '2px solid #d1d5db',
        borderRadius: '8px',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        <div style={{
          padding: '12px 16px',
          backgroundColor: '#f9fafb',
          borderBottom: '1px solid #e5e7eb',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <div style={{
            width: '16px',
            height: '16px',
            borderRadius: '4px',
            backgroundColor: '#6b7280',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '10px',
            color: 'white',
            fontWeight: 'bold'
          }}>▶</div>
          <h3 style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#374151',
            margin: 0
          }}>Output</h3>
        </div>
        <div style={{
          flex: 1,
          padding: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#6b7280'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>🚀</div>
            <p style={{
              fontSize: '14px',
              margin: 0,
              color: '#6b7280'
            }}>Click "Run" to execute your code</p>
          </div>
        </div>
      </div>
    );
  }

  const hasError = result.exit_code !== 0 || result.error;
  const hasOutput = result.stdout || result.stderr;

  return (
    <div style={{
      height: '100%',
      backgroundColor: 'white',
      border: hasError ? '2px solid #f87171' : '2px solid #34d399',
      borderRadius: '8px',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '12px 16px',
        backgroundColor: hasError ? '#fef2f2' : '#ecfdf5',
        borderBottom: hasError ? '1px solid #fecaca' : '1px solid #a7f3d0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <div style={{
            width: '16px',
            height: '16px',
            borderRadius: '50%',
            backgroundColor: hasError ? '#ef4444' : '#10b981',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '10px',
            color: 'white',
            fontWeight: 'bold'
          }}>{hasError ? '✕' : '✓'}</div>
          <h3 style={{
            fontSize: '14px',
            fontWeight: '600',
            color: hasError ? '#dc2626' : '#059669',
            margin: 0
          }}>
            {hasError ? 'Execution Failed' : 'Execution Successful'}
          </h3>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          fontSize: '12px',
          color: '#6b7280'
        }}>
          <span>Time: {result.execution_time_ms}ms</span>
          <span>Memory: {Math.round(result.memory_used_kb / 1024 * 100) / 100}MB</span>
          <span>Exit Code: {result.exit_code}</span>
        </div>
      </div>

      {/* Content */}
      <div style={{
        flex: 1,
        overflow: 'auto'
      }}>
        {hasOutput ? (
          <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Stdout */}
            {result.stdout && (
              <div>
                <h4 style={{
                  fontSize: '13px',
                  fontWeight: '600',
                  color: '#374151',
                  marginBottom: '8px',
                  margin: 0
                }}>Output</h4>
                <div style={{
                  backgroundColor: '#f3f4f6',
                  borderRadius: '6px',
                  padding: '12px',
                  border: '1px solid #e5e7eb',
                  marginTop: '8px'
                }}>
                  <pre style={{
                    fontSize: '13px',
                    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace',
                    whiteSpace: 'pre-wrap',
                    color: '#111827',
                    margin: 0
                  }}>
                    {result.stdout}
                  </pre>
                </div>
              </div>
            )}

            {/* Stderr */}
            {result.stderr && (
              <div>
                <h4 style={{
                  fontSize: '13px',
                  fontWeight: '600',
                  color: '#b91c1c',
                  marginBottom: '8px',
                  margin: 0
                }}>Error Output</h4>
                <div style={{
                  backgroundColor: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: '6px',
                  padding: '12px',
                  marginTop: '8px'
                }}>
                  <pre style={{
                    fontSize: '13px',
                    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace',
                    whiteSpace: 'pre-wrap',
                    color: '#991b1b',
                    margin: 0
                  }}>
                    {result.stderr}
                  </pre>
                </div>
              </div>
            )}

            {/* Custom error */}
            {result.error && (
              <div>
                <h4 style={{
                  fontSize: '13px',
                  fontWeight: '600',
                  color: '#b91c1c',
                  marginBottom: '8px',
                  margin: 0
                }}>Execution Error</h4>
                <div style={{
                  backgroundColor: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: '6px',
                  padding: '12px',
                  marginTop: '8px'
                }}>
                  <pre style={{
                    fontSize: '13px',
                    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace',
                    whiteSpace: 'pre-wrap',
                    color: '#991b1b',
                    margin: 0
                  }}>
                    {result.error}
                  </pre>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{
            padding: '24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#6b7280'
          }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{
                fontSize: '24px',
                marginBottom: '8px'
              }}>
                {hasError ? '❌' : '✅'}
              </div>
              <p style={{
                fontSize: '14px',
                margin: 0,
                color: '#6b7280'
              }}>
                {hasError
                  ? 'Code executed with errors but no output'
                  : 'Code executed successfully with no output'
                }
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
