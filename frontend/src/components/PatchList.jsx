import React, { useState } from 'react';
import { 
  Code, 
  Download, 
  Check, 
  X, 
  Eye, 
  FileText,
  Clock,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

const PatchList = ({ 
  patches, 
  onApplyPatch, 
  onRejectPatch, 
  onViewPatch 
}) => {
  const [selectedPatches, setSelectedPatches] = useState(new Set());
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'grid'

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
    const patchesToApply = patches.filter(p => selectedPatches.has(p.id));
    patchesToApply.forEach(patch => onApplyPatch(patch));
    setSelectedPatches(new Set());
  };

  const handleRejectSelected = () => {
    const patchesToReject = patches.filter(p => selectedPatches.has(p.id));
    patchesToReject.forEach(patch => onRejectPatch(patch));
    setSelectedPatches(new Set());
  };

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'high':
        return 'text-success-600 bg-success-100 border-success-200';
      case 'medium':
        return 'text-warning-600 bg-warning-100 border-warning-200';
      case 'low':
        return 'text-error-600 bg-error-100 border-error-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'applied':
        return <CheckCircle className="w-4 h-4 text-success-600" />;
      case 'rejected':
        return <X className="w-4 h-4 text-error-600" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-warning-600" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-600" />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (!patches || patches.length === 0) {
    return (
      <div className="card">
        <div className="card-content p-8 text-center">
          <Code className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No Patches Available
          </h3>
          <p className="text-gray-600">
            No automated patches have been generated for the current findings.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="card-title text-lg">Available Patches</h3>
              <p className="card-description">
                {patches.length} patch{patches.length !== 1 ? 'es' : ''} available for review
              </p>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setViewMode(viewMode === 'list' ? 'grid' : 'list')}
                className="btn btn-outline btn-sm"
              >
                {viewMode === 'list' ? 'Grid View' : 'List View'}
              </button>
            </div>
          </div>
        </div>
        
        {selectedPatches.size > 0 && (
          <div className="card-content pt-0">
            <div className="flex items-center justify-between p-4 bg-primary-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-primary-900">
                  {selectedPatches.size} patch{selectedPatches.size !== 1 ? 'es' : ''} selected
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleRejectSelected}
                  className="btn btn-outline btn-sm"
                >
                  <X className="w-4 h-4 mr-1" />
                  Reject Selected
                </button>
                <button
                  onClick={handleApplySelected}
                  className="btn btn-primary btn-sm"
                >
                  <Check className="w-4 h-4 mr-1" />
                  Apply Selected
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Patches List */}
      <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-4'}>
        {patches.map((patch) => (
          <div
            key={patch.id}
            className={`card cursor-pointer transition-all duration-200 ${
              selectedPatches.has(patch.id) ? 'ring-2 ring-primary-500 shadow-lg' : 'hover:shadow-md'
            }`}
            onClick={() => handleSelectPatch(patch.id)}
          >
            <div className="card-content p-0">
              {/* Header */}
              <div className="p-4 pb-3">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={selectedPatches.has(patch.id)}
                      onChange={() => handleSelectPatch(patch.id)}
                      className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                      onClick={(e) => e.stopPropagation()}
                    />
                    <h4 className="font-medium text-gray-900 truncate">
                      {patch.title}
                    </h4>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    {getStatusIcon(patch.status)}
                    <span className={`badge badge-sm ${getConfidenceColor(patch.confidence)}`}>
                      {patch.confidence}
                    </span>
                  </div>
                </div>
                
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {patch.description}
                </p>
                
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <div className="flex items-center space-x-1">
                    <FileText className="w-3 h-3" />
                    <span>{patch.changes_count} changes</span>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    <Clock className="w-3 h-3" />
                    <span>{formatFileSize(patch.diff?.length || 0)}</span>
                  </div>
                  
                  {patch.finding_id && (
                    <div className="flex items-center space-x-1">
                      <AlertCircle className="w-3 h-3" />
                      <span>Finding #{patch.finding_id}</span>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Actions */}
              <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onViewPatch(patch);
                      }}
                      className="btn btn-outline btn-sm"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </button>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        const blob = new Blob([patch.diff], { type: 'text/plain' });
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `patch-${patch.id}.diff`;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                      }}
                      className="btn btn-outline btn-sm"
                    >
                      <Download className="w-4 h-4 mr-1" />
                      Download
                    </button>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onRejectPatch(patch);
                      }}
                      className="btn btn-outline btn-sm text-error-600 hover:text-error-700"
                    >
                      <X className="w-4 h-4" />
                    </button>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onApplyPatch(patch);
                      }}
                      className="btn btn-primary btn-sm"
                    >
                      <Check className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Bulk Actions */}
      {patches.length > 1 && (
        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={handleSelectAll}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  {selectedPatches.size === patches.length ? 'Deselect All' : 'Select All'}
                </button>
                
                <span className="text-sm text-gray-500">
                  {selectedPatches.size} of {patches.length} selected
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => {
                    patches.forEach(patch => onRejectPatch(patch));
                  }}
                  className="btn btn-outline"
                >
                  <X className="w-4 h-4 mr-2" />
                  Reject All
                </button>
                
                <button
                  onClick={() => {
                    patches.forEach(patch => onApplyPatch(patch));
                  }}
                  className="btn btn-primary"
                >
                  <Check className="w-4 h-4 mr-2" />
                  Apply All
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatchList;
