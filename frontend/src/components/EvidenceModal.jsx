import React from 'react';
import { 
  X, 
  Code, 
  Image, 
  FileText, 
  ExternalLink,
  Copy,
  Check
} from 'lucide-react';

const EvidenceModal = ({ 
  isOpen, 
  onClose, 
  evidence, 
  finding 
}) => {
  const [copiedIndex, setCopiedIndex] = React.useState(null);

  if (!isOpen) return null;

  const handleCopy = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const getEvidenceIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'code':
      case 'html':
      case 'css':
      case 'javascript':
        return <Code className="w-5 h-5 text-blue-600" />;
      case 'image':
      case 'screenshot':
        return <Image className="w-5 h-5 text-green-600" />;
      case 'text':
      case 'description':
        return <FileText className="w-5 h-5 text-gray-600" />;
      default:
        return <FileText className="w-5 h-5 text-gray-600" />;
    }
  };

  const formatCode = (code, language = 'text') => {
    if (!code) return '';
    
    // Simple syntax highlighting for common languages
    if (language === 'html' || language === 'xml') {
      return code
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }
    
    return code;
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          onClick={onClose}
        />
        
        {/* Modal */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          {/* Header */}
          <div className="bg-white px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  Evidence Details
                </h3>
                {finding && (
                  <p className="text-sm text-gray-600 mt-1">
                    {finding.title || finding.message || 'Untitled Finding'}
                  </p>
                )}
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>
          
          {/* Content */}
          <div className="bg-white px-6 py-4 max-h-96 overflow-y-auto">
            {evidence && evidence.length > 0 ? (
              <div className="space-y-6">
                {evidence.map((item, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        {getEvidenceIcon(item.type)}
                        <h4 className="font-medium text-gray-900">
                          {item.type || 'Evidence'} {index + 1}
                        </h4>
                      </div>
                      <button
                        onClick={() => handleCopy(item.code || item.description || '', index)}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        {copiedIndex === index ? (
                          <Check className="w-4 h-4 text-success-600" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                    
                    {item.description && (
                      <p className="text-sm text-gray-600 mb-3">
                        {item.description}
                      </p>
                    )}
                    
                    {item.code && (
                      <div className="bg-gray-50 rounded-md p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-medium text-gray-500 uppercase">
                            {item.language || 'code'}
                          </span>
                          <span className="text-xs text-gray-500">
                            {item.code.split('\n').length} lines
                          </span>
                        </div>
                        <pre className="text-sm text-gray-800 overflow-x-auto">
                          <code 
                            dangerouslySetInnerHTML={{ 
                              __html: formatCode(item.code, item.language) 
                            }}
                          />
                        </pre>
                      </div>
                    )}
                    
                    {item.url && (
                      <div className="mt-3">
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center space-x-1 text-sm text-primary-600 hover:text-primary-700"
                        >
                          <ExternalLink className="w-4 h-4" />
                          <span>View external resource</span>
                        </a>
                      </div>
                    )}
                    
                    {item.metadata && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
                          {Object.entries(item.metadata).map(([key, value]) => (
                            <div key={key}>
                              <span className="font-medium">{key}:</span>
                              <span className="ml-1">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-medium text-gray-900 mb-2">
                  No Evidence Available
                </h4>
                <p className="text-gray-600">
                  This finding doesn't have any supporting evidence.
                </p>
              </div>
            )}
          </div>
          
          {/* Footer */}
          <div className="bg-gray-50 px-6 py-3 flex items-center justify-end space-x-3">
            <button
              onClick={onClose}
              className="btn btn-outline"
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
