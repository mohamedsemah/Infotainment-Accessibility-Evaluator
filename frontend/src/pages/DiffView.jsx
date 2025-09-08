import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Eye, EyeOff, Download, RotateCcw } from 'lucide-react';
import useAppStore from '../store/useAppStore';
import apiClient from '../api/client';

const DiffView = () => {
  const {
    patches,
    patchStatus,
    patchError,
    appliedPatches,
    setPatches,
    setPatchStatus,
    setPatchError,
    setAppliedPatches,
    uploadId
  } = useAppStore();

  const [selectedPatches, setSelectedPatches] = useState(new Set());
  const [showDiffs, setShowDiffs] = useState(new Set());
  const [isApplying, setIsApplying] = useState(false);

  useEffect(() => {
    if (uploadId && patches.length === 0) {
      loadPatches();
    }
  }, [uploadId, patches.length]);

  const loadPatches = async () => {
    try {
      setPatchStatus('generating');
      const response = await apiClient.generatePatches(uploadId);
      setPatches(response.patches || []);
      setPatchStatus('success');
    } catch (error) {
      console.error('Error loading patches:', error);
      setPatchError(error.message);
      setPatchStatus('error');
    }
  };

  const handlePatchSelect = (patchId) => {
    const newSelected = new Set(selectedPatches);
    if (newSelected.has(patchId)) {
      newSelected.delete(patchId);
    } else {
      newSelected.add(patchId);
    }
    setSelectedPatches(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedPatches.size === patches.length) {
      setSelectedPatches(new Set());
    } else {
      setSelectedPatches(new Set(patches.map(p => p.id)));
    }
  };

  const handleToggleDiff = (patchId) => {
    const newShowDiffs = new Set(showDiffs);
    if (newShowDiffs.has(patchId)) {
      newShowDiffs.delete(patchId);
    } else {
      newShowDiffs.add(patchId);
    }
    setShowDiffs(newShowDiffs);
  };

  const handleApplyPatches = async () => {
    if (selectedPatches.size === 0) return;

    try {
      setIsApplying(true);
      const selectedPatchList = patches.filter(p => selectedPatches.has(p.id));
      const response = await apiClient.applyPatches(uploadId, selectedPatchList);
      
      setAppliedPatches([...appliedPatches, ...selectedPatchList]);
      setSelectedPatches(new Set());
      
      // Show success message
      console.log('Patches applied successfully');
    } catch (error) {
      console.error('Error applying patches:', error);
      setPatchError(error.message);
    } finally {
      setIsApplying(false);
    }
  };

  const handleRecheck = async () => {
    try {
      setPatchStatus('generating');
      const response = await apiClient.recheckPatches(uploadId);
      console.log('Recheck completed:', response);
      setPatchStatus('success');
    } catch (error) {
      console.error('Error rechecking patches:', error);
      setPatchError(error.message);
      setPatchStatus('error');
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-blue-600 bg-blue-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getPatchTypeColor = (type) => {
    switch (type) {
      case 'css_update': return 'bg-purple-100 text-purple-800';
      case 'html_update': return 'bg-green-100 text-green-800';
      case 'attribute_add': return 'bg-blue-100 text-blue-800';
      case 'attribute_remove': return 'bg-red-100 text-red-800';
      case 'content_update': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (patchStatus === 'generating') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Generating patches...</p>
        </div>
      </div>
    );
  }

  if (patchStatus === 'error') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Patches</h2>
          <p className="text-gray-600 mb-4">{patchError}</p>
          <button
            onClick={loadPatches}
            className="btn btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Patch Review</h1>
          <p className="text-gray-600">
            Review and apply accessibility fixes to your infotainment UI
          </p>
        </div>

        {/* Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleSelectAll}
                className="btn btn-outline"
              >
                {selectedPatches.size === patches.length ? 'Deselect All' : 'Select All'}
              </button>
              <span className="text-sm text-gray-600">
                {selectedPatches.size} of {patches.length} patches selected
              </span>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={handleRecheck}
                className="btn btn-outline"
                disabled={appliedPatches.length === 0}
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Recheck
              </button>
              <button
                onClick={handleApplyPatches}
                disabled={selectedPatches.size === 0 || isApplying}
                className="btn btn-primary"
              >
                {isApplying ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Applying...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Apply Selected Patches
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Patches List */}
        <div className="space-y-4">
          {patches.map((patch) => (
            <div
              key={patch.id}
              className={`bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden ${
                selectedPatches.has(patch.id) ? 'ring-2 ring-primary-500' : ''
              }`}
            >
              {/* Patch Header */}
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <input
                        type="checkbox"
                        checked={selectedPatches.has(patch.id)}
                        onChange={() => handlePatchSelect(patch.id)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <h3 className="text-lg font-semibold text-gray-900">
                        {patch.rationale}
                      </h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPatchTypeColor(patch.type)}`}>
                        {patch.type.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>File: {patch.file_path}</span>
                      <span>Confidence: {patch.confidence}</span>
                      {patch.risks && patch.risks.length > 0 && (
                        <span className="text-orange-600">
                          {patch.risks.length} risk{patch.risks.length > 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => handleToggleDiff(patch.id)}
                    className="btn btn-outline btn-sm"
                  >
                    {showDiffs.has(patch.id) ? (
                      <>
                        <EyeOff className="w-4 h-4 mr-2" />
                        Hide Diff
                      </>
                    ) : (
                      <>
                        <Eye className="w-4 h-4 mr-2" />
                        Show Diff
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Patch Content */}
              {showDiffs.has(patch.id) && (
                <div className="p-6 bg-gray-50">
                  <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                    <div className="bg-gray-100 px-4 py-2 border-b border-gray-200">
                      <h4 className="text-sm font-medium text-gray-900">Patch Diff</h4>
                    </div>
                    <div className="p-4">
                      <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
                        {patch.diff}
                      </pre>
                    </div>
                  </div>
                  
                  {patch.risks && patch.risks.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-medium text-orange-900 mb-2">Risks:</h4>
                      <ul className="list-disc list-inside text-sm text-orange-800">
                        {patch.risks.map((risk, index) => (
                          <li key={index}>{risk}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {patches.length === 0 && (
          <div className="text-center py-12">
            <CheckCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Patches Available</h3>
            <p className="text-gray-600">
              No accessibility fixes were generated for this upload.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DiffView;