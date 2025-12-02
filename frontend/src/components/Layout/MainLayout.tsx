import React from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';

interface MainLayoutProps {
  header: React.ReactNode;
  problemPanel: React.ReactNode;
  codeEditor: React.ReactNode;
  outputPanel: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({
  header,
  problemPanel,
  codeEditor,
  outputPanel,
}) => {
  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f8fafc' }}>
      {/* Header */}
      {header}

      {/* Main content area */}
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex' }}>
        <PanelGroup direction="horizontal">
          {/* Problem panel - 15% width ONLY */}
          <Panel defaultSize={15} minSize={10} maxSize={30}>
            <div style={{
              height: '100%',
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              backgroundColor: 'white',
              borderRight: '3px solid #e2e8f0',
              boxShadow: '2px 0 4px rgba(0, 0, 0, 0.05)',
              overflow: 'auto'
            }}>
              {problemPanel}
            </div>
          </Panel>

          <PanelResizeHandle style={{
            width: '8px',
            backgroundColor: '#cbd5e1',
            cursor: 'col-resize',
            transition: 'all 0.2s ease'
          }} />

          {/* Code editor and output - 85% width */}
          <Panel defaultSize={85}>
            <PanelGroup direction="vertical" style={{ height: '100%', width: '100%' }}>
              {/* Code editor - 60% height */}
              <Panel defaultSize={60} minSize={30}>
                <div style={{
                  height: '100%',
                  width: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  backgroundColor: 'white'
                }}>
                  <div style={{
                    height: '32px',
                    backgroundColor: '#f1f5f9',
                    borderBottom: '1px solid #e2e8f0',
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0 12px',
                    fontSize: '13px',
                    fontWeight: '600',
                    color: '#1e293b',
                    flexShrink: 0,
                    userSelect: 'none'
                  }}>
                    💻 Code Editor
                  </div>
                  <div style={{
                    flex: 1,
                    width: '100%',
                    minHeight: 0,
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column'
                  }}>
                    {codeEditor}
                  </div>
                </div>
              </Panel>

              <PanelResizeHandle style={{
                height: '8px',
                backgroundColor: '#cbd5e1',
                cursor: 'row-resize',
                transition: 'all 0.2s ease'
              }} />

              {/* Output panel - 40% height */}
              <Panel defaultSize={40} minSize={15}>
                <div style={{
                  height: '100%',
                  width: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  backgroundColor: 'white',
                  borderTop: '3px solid #e2e8f0'
                }}>
                  <div style={{
                    height: '32px',
                    backgroundColor: '#f1f5f9',
                    borderBottom: '1px solid #e2e8f0',
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0 12px',
                    fontSize: '13px',
                    fontWeight: '600',
                    color: '#1e293b',
                    flexShrink: 0,
                    userSelect: 'none'
                  }}>
                    📟 Output
                  </div>
                  <div style={{
                    flex: 1,
                    width: '100%',
                    minHeight: 0,
                    overflow: 'auto'
                  }}>
                    {outputPanel}
                  </div>
                </div>
              </Panel>
            </PanelGroup>
          </Panel>
        </PanelGroup>
      </div>
    </div>
  );
};
