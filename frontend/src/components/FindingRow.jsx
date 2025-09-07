import React, { useState } from 'react';
import { 
  MapPin, 
  ExternalLink, 
  Code, 
  Image, 
  FileText,
  ChevronRight,
  Eye
} from 'lucide-react';

const FindingRow = ({ finding, cluster, onSelect }) => {
  const [isHovered, setIsHovered] = useState(false);

  const getFileIcon = (filePath) => {
    const extension = filePath.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'html':
      case 'htm':
        return <FileText className="w-4 h-4 text-blue-600" />;
      case 'css':
        return <Code className="w-4 h-4 text-pink-600" />;
      case 'js':
      case 'jsx':
      case 'ts':
      case 'tsx':
        return <Code className="w-4 h-4 text-yellow-600" />;
      case 'qml':
        return <Code className="w-4 h-4 text-purple-600" />;
      case 'xml':
        return <FileText className="w-4 h-4 text-green-600" />;
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'gif':
      case 'svg':
        return <Image className="w-4 h-4 text-green-600" />;
      default:
        return <FileText className="w-4 h-4 text-gray-600" />;
    }
  };

  const formatLocation = (location) => {
    if (!location) return 'Unknown location';
    
    const parts = [];
    if (location.file) {
      parts.push(location.file.split('/').pop());
    }
    if (location.line) {
      parts.push(`line ${location.line}`);
    }
    if (location.column) {
      parts.push(`col ${location.column}`);
    }
    
    return parts.join(', ');
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'text-error-600 bg-error-50 border-error-200';
      case 'high':
        return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'medium':
        return 'text-primary-600 bg-primary-50 border-primary-200';
      case 'low':
        return 'text-gray-600 bg-gray-50 border-gray-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const handleClick = () => {
    onSelect(finding);
  };

  return (
    <div
      className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 ${
        isHovered ? 'shadow-sm bg-gray-50' : 'bg-white'
      } ${getSeverityColor(finding.severity || cluster.severity)}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-start space-x-3 flex-1 min-w-0">
          {/* File Icon */}
          <div className="flex-shrink-0 mt-1">
            {getFileIcon(finding.location?.file || '')}
          </div>
          
          {/* Finding Details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-1">
              <h5 className="font-medium text-gray-900 truncate">
                {finding.title || finding.message || 'Untitled Finding'}
              </h5>
              {finding.severity && (
                <span className={`badge badge-sm ${getSeverityColor(finding.severity)}`}>
                  {finding.severity}
                </span>
              )}
            </div>
            
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <MapPin className="w-3 h-3" />
                <span className="truncate">
                  {formatLocation(finding.location)}
                </span>
              </div>
              
              {finding.element && (
                <div className="flex items-center space-x-1">
                  <Code className="w-3 h-3" />
                  <span className="truncate">
                    {finding.element}
                  </span>
                </div>
              )}
              
              {finding.confidence && (
                <div className="flex items-center space-x-1">
                  <span className="text-gray-500">Confidence:</span>
                  <span className={`font-medium ${
                    finding.confidence === 'high' ? 'text-success-600' :
                    finding.confidence === 'medium' ? 'text-warning-600' :
                    'text-error-600'
                  }`}>
                    {finding.confidence}
                  </span>
                </div>
              )}
            </div>
            
            {finding.description && (
              <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                {finding.description}
              </p>
            )}
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center space-x-2 ml-4">
          {finding.evidence && finding.evidence.length > 0 && (
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              <span>{finding.evidence.length}</span>
              <span>evidence</span>
            </div>
          )}
          
          <div className="flex items-center space-x-1">
            <Eye className="w-4 h-4 text-gray-400" />
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </div>
        </div>
      </div>
      
      {/* Evidence Preview */}
      {finding.evidence && finding.evidence.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="text-xs text-gray-500 mb-2">Evidence:</div>
          <div className="space-y-1">
            {finding.evidence.slice(0, 2).map((evidence, index) => (
              <div key={index} className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                <div className="font-mono text-xs text-gray-500 mb-1">
                  {evidence.type}: {evidence.description}
                </div>
                {evidence.code && (
                  <div className="font-mono text-xs text-gray-800">
                    {evidence.code}
                  </div>
                )}
              </div>
            ))}
            {finding.evidence.length > 2 && (
              <div className="text-xs text-gray-500">
                ... and {finding.evidence.length - 2} more evidence items
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FindingRow;
