import React, { useState } from 'react';
import { CheckCircle, XCircle, Eye, EyeOff, Download, AlertTriangle } from 'lucide-react';

const PatchList = ({ patches, onApplyPatch, onRejectPatch, onViewDiff }) => {
  const [expandedPatches, setExpandedPatches] = useState(new Set());
  const [selectedPatches, setSelectedPatches] = useState(new Set());

  const handleToggleExpanded = (patchId) => {
    const newExpanded = new Set(expandedPatches);
    if (newExpanded.has(patchId)) {
      newExpanded.delete(patchId);
    } else {
      newExpanded.add(patchId);
    }
    setExpandedPatches(newExpanded);
  };

  const handleSelectPatch = (patchId) => {
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

  const handleApplySelected = () => {
    selectedPatches.forEach(patchId => {
      const patch = patches.find(p => p.id === patchId);
      if (patch && onApplyPatch) {
        onApplyPatch(patch);
      }
    });
    setSelectedPatches(new Set());
  };

  const getPatchTypeColor = (type) => {
    switch (type) {
      case 'css_update':
        return 'bg-purple-100 text-purple-800';
      case 'html_update':
        return 'bg-green-100 text-green-800';
      case 'attribute_add':
        return 'bg-blue-100 text-blue-800';
      case 'attribute_remove':
        return 'bg-red-100 text-red-800';
      case 'content_update':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'high':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  if (patches.length === 0) {
    return (
      <div className="text-center py-8">
        <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Patches Available</h3>
        <p className="text-gray-600">
          No accessibility fixes were generated for this upload.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={handleSelectAll}
            className="btn btn-outline btn-sm"
          >
            {selectedPatches.size === patches.length ? 'Deselect All' : 'Select All'}
          </button>
          <span className="text-sm text-gray-600">
            {selectedPatches.size} of {patches.length} patches selected
          </span>
        </div>
        <button
          onClick={handleApplySelected}
          disabled={selectedPatches.size === 0}
          className="btn btn-primary btn-sm"
        >
          Apply Selected ({selectedPatches.size})
        </button>
      </div>

      {/* Patches List */}
      <div className="space-y-3">
        {patches.map((patch) => {
          const isExpanded = expandedPatches.has(patch.id);
          const isSelected = selectedPatches.has(patch.id);
          const hasRisks = patch.risks && patch.risks.length > 0;

          return (
            <div
              key={patch.id}
              className={`bg-white rounded-lg border transition-all ${
                isSelected ? 'ring-2 ring-primary-500 border-primary-300' : 'border-gray-200'
              }`}
            >
              {/* Patch Header */}
              <div className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleSelectPatch(patch.id)}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded mt-1"
                    />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="font-medium text-gray-900">{patch.rationale}</h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPatchTypeColor(patch.type)}`}>
                          {patch.type.replace('_', ' ').toUpperCase()}
                        </span>
                        {hasRisks && (
                          <span className="flex items-center text-orange-600 text-xs">
                            <AlertTriangle className="w-3 h-3 mr-1" />
                            {patch.risks.length} risk{patch.risks.length > 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span>File: {patch.file_path}</span>
                        <span className={`font-medium ${getConfidenceColor(patch.confidence)}`}>
                          Confidence: {patch.confidence}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleToggleExpanded(patch.id)}
                      className="btn btn-outline btn-sm"
                    >
                      {isExpanded ? (
                        <>
                          <EyeOff className="w-4 h-4 mr-1" />
                          Hide
                        </>
                      ) : (
                        <>
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => onApplyPatch && onApplyPatch(patch)}
                      className="btn btn-primary btn-sm"
                    >
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Apply
                    </button>
                    <button
                      onClick={() => onRejectPatch && onRejectPatch(patch)}
                      className="btn btn-outline btn-sm text-red-600 hover:text-red-700"
                    >
                      <XCircle className="w-4 h-4 mr-1" />
                      Reject
                    </button>
                  </div>
                </div>
              </div>

              {/* Expanded Content */}
              {isExpanded && (
                <div className="px-4 pb-4 border-t border-gray-200">
                  <div className="pt-4 space-y-4">
                    {/* Patch Diff */}
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Patch Diff</h4>
                      <div className="bg-gray-50 rounded-lg p-3 border">
                        <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono overflow-x-auto">
                          {patch.diff}
                        </pre>
                      </div>
                    </div>

                    {/* Risks */}
                    {hasRisks && (
                      <div>
                        <h4 className="text-sm font-medium text-orange-700 mb-2">Risks</h4>
                        <ul className="list-disc list-inside text-sm text-orange-800 space-y-1">
                          {patch.risks.map((risk, index) => (
                            <li key={index}>{risk}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex items-center justify-between pt-2">
                      <div className="text-xs text-gray-500">
                        Created: {new Date(patch.created_at).toLocaleString()}
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => onViewDiff && onViewDiff(patch)}
                          className="btn btn-outline btn-xs"
                        >
                          <Download className="w-3 h-3 mr-1" />
                          Download Diff
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PatchList;