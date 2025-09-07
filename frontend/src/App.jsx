import React from 'react';
import useAppStore from './store/useAppStore';

// Import pages
import UploadPage from './pages/Upload';
import ResultsPage from './pages/Results';
import DiffViewPage from './pages/DiffView';
import ReportPage from './pages/Report';
import SettingsPage from './pages/Settings';

function App() {
  const { theme, currentPage } = useAppStore();

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'upload':
        return <UploadPage />;
      case 'results':
        return <ResultsPage />;
      case 'diff':
        return <DiffViewPage />;
      case 'report':
        return <ReportPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <UploadPage />;
    }
  };

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
      {renderCurrentPage()}
    </div>
  );
}

export default App;
