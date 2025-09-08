import React from 'react';
import { X, Eye, Code, Image, BarChart3 } from 'lucide-react';

const EvidenceModal = ({ isOpen, onClose, evidence }) => {
  if (!isOpen || !evidence) return null;

  const renderEvidenceContent = () => {
    if (!evidence) return null;

    return (
      <div className="space-y-4">
        {/* File Information */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-2">File Information</h4>
          <div className="text-sm text-gray-600">
            <p><strong>File:</strong> {evidence.file_path}</p>
            {evidence.line_number && (
              <p><strong>Line:</strong> {evidence.line_number}</p>
            )}
            {evidence.column_number && (
              <p><strong>Column:</strong> {evidence.column_number}</p>
            )}
          </div>
        </div>

        {/* Code Snippet */}
        {evidence.code_snippet && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2 flex items-center">
              <Code className="w-4 h-4 mr-2" />
              Code Snippet
            </h4>
            <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono bg-white p-3 rounded border overflow-x-auto">
              {evidence.code_snippet}
            </pre>
          </div>
        )}

        {/* Metrics */}
        {evidence.metrics && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2 flex items-center">
              <BarChart3 className="w-4 h-4 mr-2" />
              Metrics
            </h4>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(evidence.metrics).map(([key, value]) => (
                <div key={key} className="bg-white p-3 rounded border">
                  <div className="text-xs text-gray-500 uppercase tracking-wide">
                    {key.replace(/_/g, ' ')}
                  </div>
                  <div className="text-sm font-medium text-gray-900">
                    {typeof value === 'number' ? value.toFixed(2) : String(value)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Before/After Values */}
        {(evidence.before_value || evidence.after_value) && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Before/After Comparison</h4>
            <div className="grid grid-cols-2 gap-4">
              {evidence.before_value && (
                <div className="bg-white p-3 rounded border">
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">
                    Before
                  </div>
                  <div className="text-sm font-mono text-gray-900">
                    {evidence.before_value}
                  </div>
                </div>
              )}
              {evidence.after_value && (
                <div className="bg-white p-3 rounded border">
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">
                    After
                  </div>
                  <div className="text-sm font-mono text-gray-900">
                    {evidence.after_value}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Screenshot */}
        {evidence.screenshot_path && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2 flex items-center">
              <Image className="w-4 h-4 mr-2" />
              Screenshot
            </h4>
            <div className="bg-white p-3 rounded border">
              <img
                src={evidence.screenshot_path}
                alt="Evidence screenshot"
                className="max-w-full h-auto rounded"
              />
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          onClick={onClose}
        />

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Evidence Details
              </h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="max-h-96 overflow-y-auto">
              {renderEvidenceContent()}
            </div>
          </div>
          
          <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              onClick={onClose}
              className="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvidenceModal;