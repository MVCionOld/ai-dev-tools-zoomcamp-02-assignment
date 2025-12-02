import React, { useRef, useEffect, useState } from 'react';
import { Editor } from '@monaco-editor/react';
import type { editor } from 'monaco-editor';

interface MonacoEditorProps {
  value: string;
  language: string;
  onChange?: (value: string) => void;
  onCursorChange?: (line: number, column: number) => void;
  onRemoteChange?: (value: string) => void;
  readOnly?: boolean;
  theme?: 'vs' | 'vs-dark' | 'hc-black';
  shareDBEnabled?: boolean;
  sendOperation?: (type: 'insert' | 'delete', position: number, content?: string) => Promise<boolean>;
  sendCursor?: (position: { line: number; column: number }, selection?: any) => void;
}

export const MonacoEditor: React.FC<MonacoEditorProps> = ({
  value,
  language,
  onChange,
  onCursorChange,
  onRemoteChange,
  readOnly = false,
  theme = 'vs',
  shareDBEnabled = false,
  sendOperation,
  sendCursor,
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const lastValueRef = useRef<string>(value);
  const isRemoteChangeRef = useRef<boolean>(false);
  const [version, setVersion] = useState(0);

  const handleEditorDidMount = (editor: editor.IStandaloneCodeEditor) => {
    editorRef.current = editor;

    // Listen for cursor position changes
    editor.onDidChangeCursorPosition((e) => {
      const position = { line: e.position.lineNumber, column: e.position.column };
      onCursorChange?.(e.position.lineNumber, e.position.column);

      // Send cursor position to other users via ShareDB presence
      if (sendCursor) {
        const selection = editor.getSelection();
        const selectionData = selection ? {
          start: { line: selection.startLineNumber, column: selection.startColumn },
          end: { line: selection.endLineNumber, column: selection.endColumn }
        } : undefined;
        sendCursor(position, selectionData);
      }
    });

    // Listen for content changes to implement ShareDB
    if (shareDBEnabled && sendOperation) {
      editor.onDidChangeModelContent((e) => {
        if (isRemoteChangeRef.current) {
          isRemoteChangeRef.current = false;
          return;
        }

        const newValue = editor.getValue();
        const oldValue = lastValueRef.current;

        // Determine what changed
        if (newValue.length > oldValue.length) {
          // Insert operation
          const insertedText = newValue.slice(
            oldValue.length > 0 ? oldValue.length - 1 : 0
          );
          const position = e.changes[0]?.rangeOffset || 0;
          const insertedContent = newValue.slice(position, position + (newValue.length - oldValue.length));

          sendOperation('insert', position, insertedContent);
        } else if (newValue.length < oldValue.length) {
          // Delete operation
          const position = e.changes[0]?.rangeOffset || 0;
          const deletedLength = oldValue.length - newValue.length;
          const deletedContent = oldValue.slice(position, position + deletedLength);

          sendOperation('delete', position, deletedContent);
        }

        lastValueRef.current = newValue;
        onChange?.(newValue);
      });
    }

    // Configure editor options for better UX
    editor.updateOptions({
      fontSize: 15,
      fontFamily: 'Roboto Mono, Fira Code, Monaco, Menlo, Consolas, monospace',
      lineNumbers: 'on',
      minimap: { enabled: true, maxColumn: 80 },
      scrollBeyondLastLine: false,
      automaticLayout: true,
      tabSize: 4,
      insertSpaces: true,
      wordWrap: 'on',
      lineHeight: 22,
      padding: { top: 20, bottom: 20 },
      readOnly,
      cursorBlinking: 'smooth',
      cursorSmoothCaretAnimation: 'on',
      smoothScrolling: true,
      contextmenu: true,
      selectOnLineNumbers: true,
      roundedSelection: false,
      renderLineHighlight: 'all',
      bracketPairColorization: { enabled: true },
      guides: {
        bracketPairs: true,
        indentation: true
      },
      suggest: {
        showMethods: true,
        showFunctions: true,
        showConstructors: true,
        showFields: true,
        showVariables: true
      },
      quickSuggestions: {
        other: true,
        comments: true,
        strings: true
      }
    });

    // Add focus border effect
    editor.onDidFocusEditorWidget(() => {
      const container = editor.getContainerDomNode();
      if (container) {
        container.style.boxShadow = '0 0 0 2px #1a73e8';
        container.style.borderRadius = '4px';
      }
    });

    editor.onDidBlurEditorWidget(() => {
      const container = editor.getContainerDomNode();
      if (container) {
        container.style.boxShadow = 'none';
      }
    });
  };

  const handleEditorChange = (value: string | undefined) => {
    onChange?.(value || '');
  };

  // Handle remote changes
  useEffect(() => {
    if (onRemoteChange && editorRef.current && value !== lastValueRef.current) {
      isRemoteChangeRef.current = true;
      const currentSelection = editorRef.current.getSelection();
      editorRef.current.setValue(value);

      // Restore cursor position if it was set
      if (currentSelection) {
        editorRef.current.setSelection(currentSelection);
      }

      lastValueRef.current = value;
    }
  }, [value, onRemoteChange]);

  // Get language mode for Monaco
  const getMonacoLanguage = (lang: string): string => {
    switch (lang) {
      case 'python3.13':
        return 'python';
      case 'javascript':
        return 'javascript';
      case 'sql-postgres':
      case 'sql-mysql':
      case 'sql-sqlite':
        return 'sql';
      default:
        return 'plaintext';
    }
  };

  return (
    <div
      className="h-full w-full border border-gray-200 rounded-lg overflow-hidden"
      style={{
        display: 'flex',
        flexDirection: 'column',
        minWidth: 0,
        minHeight: 0,
        flex: 1,
        width: '100%',
        height: '100%'
      }}
    >
      <Editor
        width="100%"
        height="100%"
        language={getMonacoLanguage(language)}
        value={value}
        theme={theme}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        options={{
          readOnly,
          automaticLayout: true,
        }}
      />
    </div>
  );
};
