import React, { useState } from 'react';
import { 
  ChevronDown, 
  ChevronRight, 
  AlertTriangle, 
  Info, 
  CheckCircle,
  Eye,
  Code,
  FileText
} from 'lucide-react';
import FindingRow from './FindingRow';

const ClusterCard = ({ 
  cluster, 
  isSelected, 
  onSelect, 
  onFindingSelect 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <AlertTriangle className="w-5 h-5 text-error-600" />;
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-warning-600" />;
      case 'medium':
        return <Info className="w-5 h-5 text-primary-600" />;
      case 'low':
        return <Info className="w-5 h-5 text-gray-600" />;
      default:
        return <Info className="w-5 h-5 text-gray-600" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'border-error-200 bg-error-50';
      case 'high':
        return 'border-warning-200 bg-warning-50';
      case 'medium':
        return 'border-primary-200 bg-primary-50';
      case 'low':
        return 'border-gray-200 bg-gray-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'high':
        return 'text-success-600 bg-success-100';
      case 'medium':
        return 'text-warning-600 bg-warning-100';
      case 'low':
        return 'text-error-600 bg-error-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const handleToggle = () => {
    setIsExpanded(!isExpanded);
  };

  const handleCardClick = () => {
    onSelect(cluster);
  };

  return (
    <div 
      className={`card cursor-pointer transition-all duration-200 ${
        isSelected ? 'ring-2 ring-primary-500 shadow-lg' : 'hover:shadow-md'
      } ${getSeverityColor(cluster.severity)}`}
      onClick={handleCardClick}
    >
      <div className="card-content p-0">
        {/* Header */}
        <div className="p-6 pb-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              <div className="flex-shrink-0 mt-1">
                {getSeverityIcon(cluster.severity)}
              </div>
              
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {cluster.summary}
                </h3>
                
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {cluster.summary}
                </p>
                
                <div className="flex items-center space-x-4 text-sm">
                  <div className="flex items-center space-x-1">
                    <span className="text-gray-500">Agent:</span>
                    <span className="font-medium text-gray-900 capitalize">
                      {(cluster.occurrences[0]?.agent || 'unknown').replace('_', ' ')}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    <span className="text-gray-500">WCAG:</span>
                    <span className="font-medium text-gray-900">
                      {cluster.wcag_criterion}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    <span className="text-gray-500">Occurrences:</span>
                    <span className="font-medium text-gray-900">
                      {cluster.occurrences.length}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2 ml-4">
              <span className={`badge ${getConfidenceColor(cluster.confidence)}`}>
                {cluster.confidence} confidence
              </span>
              
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleToggle();
                }}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                {isExpanded ? (
                  <ChevronDown className="w-5 h-5" />
                ) : (
                  <ChevronRight className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Expanded Content */}
        {isExpanded && (
          <div className="border-t border-gray-200 bg-white">
            <div className="p-6">
              {/* Cluster Details */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-3">Cluster Details</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Root Cause:</span>
                    <p className="font-medium text-gray-900 mt-1">
                      {cluster.root_cause}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Impact:</span>
                    <p className="font-medium text-gray-900 mt-1">
                      {cluster.impact}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Priority:</span>
                    <p className="font-medium text-gray-900 mt-1">
                      {cluster.priority}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Status:</span>
                    <p className="font-medium text-gray-900 mt-1">
                      {cluster.status}
                    </p>
                  </div>
                </div>
              </div>

              {/* Individual Findings */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">
                    Individual Findings ({cluster.occurrences.length})
                  </h4>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <Eye className="w-4 h-4" />
                    <span>Click to view details</span>
                  </div>
                </div>
                
                <div className="space-y-2">
                  {cluster.occurrences.map((finding, index) => (
                    <FindingRow
                      key={finding.id || index}
                      finding={finding}
                      cluster={cluster}
                      onSelect={() => onFindingSelect(finding)}
                    />
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <FileText className="w-4 h-4" />
                    <span>Available actions: View patches, Export findings</span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button className="btn btn-outline btn-sm">
                      <Code className="w-4 h-4 mr-1" />
                      View Patches
                    </button>
                    <button className="btn btn-primary btn-sm">
                      <Eye className="w-4 h-4 mr-1" />
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClusterCard;
