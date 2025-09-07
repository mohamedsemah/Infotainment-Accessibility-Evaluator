import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  Download, 
  Check, 
  X, 
  Eye, 
  Code,
  FileText,
  AlertCircle
} from 'lucide-react';
// Simple diff viewer component
import useAppStore from '../store/useAppStore';

const DiffViewPage = () => {
  const {
    selectedFinding,
    patches,
    setCurrentPage
  } = useAppStore();

  const [selectedPatch, setSelectedPatch] = useState(null);
  const [viewMode, setViewMode] = useState('unified'); // 'unified' or 'split'

  useEffect(() => {
    if (patches.length > 0 && !selectedPatch) {
      setSelectedPatch(patches[0]);
    }
  }, [patches, selectedPatch]);

  const handleBack = () => {
    setCurrentPage('results');
  };

  const handleApplyPatch = (patch) => {
    // Apply patch logic would go here
    console.log('Applying patch:', patch.id);
  };

  const handleRejectPatch = (patch) => {
    // Reject patch logic would go here
    console.log('Rejecting patch:', patch.id);
  };

  const handleDownloadPatch = (patch) => {
    const blob = new Blob([patch.diff], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `patch-${patch.id}.diff`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  if (!selectedFinding) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-warning-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Finding Selected</h2>
          <p className="text-gray-600 mb-6">Please select a finding to view its patches.</p>
          <button
            onClick={handleBack}
            className="btn btn-primary"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Results
          </button>
        </div>
      </div>
    );
  }

  const relatedPatches = patches.filter(patch => 
    patch.finding_id === selectedFinding.id
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleBack}
                className="text-gray-400 hover:text-gray-600"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Patch Preview
                </h1>
                <p className="text-sm text-gray-600">
                  {selectedFinding.title}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setViewMode('unified')}
                  className={`btn btn-sm ${viewMode === 'unified' ? 'btn-primary' : 'btn-outline'}`}
                >
                  <FileText className="w-4 h-4 mr-1" />
                  Unified
                </button>
                <button
                  onClick={() => setViewMode('split')}
                  className={`btn btn-sm ${viewMode === 'split' ? 'btn-primary' : 'btn-outline'}`}
                >
                  <Code className="w-4 h-4 mr-1" />
                  Split
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Patches List */}
          <div className="lg:col-span-1">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title text-lg">Available Patches</h3>
                <p className="card-description">
                  {relatedPatches.length} patch{relatedPatches.length !== 1 ? 'es' : ''} available
                </p>
              </div>
              <div className="card-content p-0">
                <div className="divide-y divide-gray-200">
                  {relatedPatches.map((patch) => (
                    <div
                      key={patch.id}
                      className={`p-4 cursor-pointer hover:bg-gray-50 ${
                        selectedPatch?.id === patch.id ? 'bg-primary-50 border-r-2 border-primary-500' : ''
                      }`}
                      onClick={() => setSelectedPatch(patch)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 mb-1">
                            {patch.title}
                          </h4>
                          <p className="text-sm text-gray-600 mb-2">
                            {patch.description}
                          </p>
                          <div className="flex items-center space-x-2">
                            <span className={`badge badge-sm ${
                              patch.confidence === 'high' ? 'badge-success' :
                              patch.confidence === 'medium' ? 'badge-warning' :
                              'badge-error'
                            }`}>
                              {patch.confidence} confidence
                            </span>
                            <span className="text-xs text-gray-500">
                              {patch.changes_count} changes
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Diff Viewer */}
          <div className="lg:col-span-2">
            {selectedPatch ? (
              <div className="card">
                <div className="card-header">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="card-title text-lg">{selectedPatch.title}</h3>
                      <p className="card-description">{selectedPatch.description}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleDownloadPatch(selectedPatch)}
                        className="btn btn-outline btn-sm"
                      >
                        <Download className="w-4 h-4 mr-1" />
                        Download
                      </button>
                    </div>
                  </div>
                </div>
                <div className="card-content p-0">
                  <div className="border-t border-gray-200">
                    <div className="p-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Original</h4>
                          <pre className="bg-gray-50 p-3 rounded text-sm font-mono overflow-x-auto">
                            {selectedPatch.old_content || 'No original content'}
                          </pre>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Patched</h4>
                          <pre className="bg-green-50 p-3 rounded text-sm font-mono overflow-x-auto">
                            {selectedPatch.new_content || 'No patched content'}
                          </pre>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="card-footer">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">
                        Confidence: <strong>{selectedPatch.confidence}</strong>
                      </span>
                      <span className="text-sm text-gray-600">
                        • {selectedPatch.changes_count} changes
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleRejectPatch(selectedPatch)}
                        className="btn btn-outline btn-sm"
                      >
                        <X className="w-4 h-4 mr-1" />
                        Reject
                      </button>
                      <button
                        onClick={() => handleApplyPatch(selectedPatch)}
                        className="btn btn-primary btn-sm"
                      >
                        <Check className="w-4 h-4 mr-1" />
                        Apply Patch
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="card">
                <div className="card-content p-12 text-center">
                  <Eye className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    No Patches Available
                  </h3>
                  <p className="text-gray-600">
                    No automated patches are available for this finding.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiffViewPage;
