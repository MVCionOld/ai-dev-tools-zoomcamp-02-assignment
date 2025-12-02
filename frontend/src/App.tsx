
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SessionList } from './components/Session/SessionList';
import { SessionView } from './components/Session/SessionView';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            {/* Home page - Session list */}
            <Route path="/" element={<SessionList />} />

            {/* Session view */}
            <Route path="/session/:sessionId" element={<SessionView />} />

            {/* Redirect any other routes to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
