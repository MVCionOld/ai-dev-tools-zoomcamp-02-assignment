import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ProblemEditorProps {
  initialValue: string;
  onSave: (value: string) => void;
  onCancel: () => void;
  isSaving?: boolean;
}

export const ProblemEditor: React.FC<ProblemEditorProps> = ({
  initialValue,
  onSave,
  onCancel,
  isSaving = false,
}) => {
  const [value, setValue] = useState(initialValue);
  const [showPreview, setShowPreview] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const handleSave = () => {
    onSave(value.trim());
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Ctrl/Cmd + S to save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      handleSave();
    }

    // Escape to cancel
    if (e.key === 'Escape') {
      onCancel();
    }
  };

  return (
    <div style={{
      height: '100%',
      backgroundColor: 'white',
      border: '2px solid #1a73e8',
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
        borderBottom: '2px solid #dbeafe',
        backgroundColor: '#dbeafe'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#1e40af', margin: 0 }}>✏️ Edit Problem Statement</h2>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: '#f1f5f9',
            borderRadius: '8px',
            padding: '4px'
          }}>
            <button
              onClick={() => setShowPreview(false)}
              style={{
                padding: '6px 12px',
                fontSize: '14px',
                borderRadius: '6px',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                backgroundColor: !showPreview ? 'white' : 'transparent',
                color: !showPreview ? '#1f2937' : '#6b7280',
                fontWeight: !showPreview ? '500' : '400',
                boxShadow: !showPreview ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
              }}
            >
              Write
            </button>
            <button
              onClick={() => setShowPreview(true)}
              style={{
                padding: '6px 12px',
                fontSize: '14px',
                borderRadius: '6px',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                backgroundColor: showPreview ? 'white' : 'transparent',
                color: showPreview ? '#1f2937' : '#6b7280',
                fontWeight: showPreview ? '500' : '400',
                boxShadow: showPreview ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
              }}
            >
              Preview
            </button>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={onCancel}
            style={{
              backgroundColor: '#f1f5f9',
              color: '#374151',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '14px',
              padding: '6px 12px',
              cursor: 'pointer',
              fontWeight: '500',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#e2e8f0'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#f1f5f9'}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || !value.trim()}
            style={{
              backgroundColor: isSaving || !value.trim() ? '#9ca3af' : '#1a73e8',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              padding: '6px 12px',
              cursor: isSaving || !value.trim() ? 'not-allowed' : 'pointer',
              fontWeight: '500',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => {
              if (!isSaving && value.trim()) {
                e.currentTarget.style.backgroundColor = '#1557b0';
              }
            }}
            onMouseOut={(e) => {
              if (!isSaving && value.trim()) {
                e.currentTarget.style.backgroundColor = '#1a73e8';
              }
            }}
          >
            {isSaving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        {showPreview ? (
          /* Preview Mode */
          <div style={{ height: '100%', overflowY: 'auto', padding: '20px' }}>
            <div style={{ maxWidth: 'none', fontSize: '15px', lineHeight: '1.6', color: '#374151' }}>
              {value.trim() ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {value}
                </ReactMarkdown>
              ) : (
                <p style={{ color: '#6b7280', fontStyle: 'italic' }}>Nothing to preview yet...</p>
              )}
            </div>
          </div>
        ) : (
          /* Edit Mode */
          <div style={{ height: '100%', padding: '16px' }}>
            <textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="# Problem Title

Describe your coding problem here...

## Example

```python
def solution():
    pass
```

**Input:**
**Output:**
**Constraints:**
"
              style={{
                width: '100%',
                height: '100%',
                resize: 'none',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                padding: '12px',
                fontFamily: 'ui-monospace, SFMono-Regular, Monaco, Consolas, monospace',
                fontSize: '14px',
                lineHeight: '1.6',
                backgroundColor: '#fafafa',
                color: '#374151',
                outline: 'none'
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = '#1a73e8';
                e.currentTarget.style.boxShadow = '0 0 0 3px rgba(26, 115, 232, 0.1)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = '#d1d5db';
                e.currentTarget.style.boxShadow = 'none';
              }}
            />
          </div>
        )}
      </div>

      {/* Help text */}
      <div style={{
        padding: '12px 16px',
        backgroundColor: '#f8fafc',
        borderTop: '1px solid #e2e8f0',
        fontSize: '12px',
        color: '#64748b'
      }}>
        <p style={{ margin: 0 }}>
          Supports GitHub-flavored Markdown.
          Press <kbd style={{
            padding: '2px 6px',
            backgroundColor: '#e2e8f0',
            borderRadius: '3px',
            fontFamily: 'monospace',
            fontSize: '11px'
          }}>Ctrl+S</kbd> to save,
          <kbd style={{
            padding: '2px 6px',
            backgroundColor: '#e2e8f0',
            borderRadius: '3px',
            fontFamily: 'monospace',
            fontSize: '11px'
          }}>Esc</kbd> to cancel.
        </p>
      </div>
    </div>
  );
};
