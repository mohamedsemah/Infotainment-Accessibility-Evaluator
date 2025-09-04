import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import UploadPage from '@/pages/UploadPage';
import ResultsPage from '@/pages/ResultsPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/results/:sessionId" element={<ResultsPage />} />
        </Routes>
        <Toaster />
      </div>
    </Router>
  );
}

export default App;
