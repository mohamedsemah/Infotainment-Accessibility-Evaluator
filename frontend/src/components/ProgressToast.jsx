import React from 'react';
import { 
  Loader2, 
  CheckCircle, 
  AlertCircle, 
  X,
  Clock,
  Zap
} from 'lucide-react';

const ProgressToast = ({ 
  progress, 
  step, 
  isVisible = true, 
  onClose,
  type = 'processing' // 'processing', 'success', 'error'
}) => {
  if (!isVisible) return null;

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-success-600" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-error-600" />;
      default:
        return <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />;
    }
  };

  const getTitle = () => {
    switch (type) {
      case 'success':
        return 'Analysis Complete';
      case 'error':
        return 'Analysis Failed';
      default:
        return 'Processing Analysis';
    }
  };

  const getStepIcon = (stepName) => {
    if (stepName?.toLowerCase().includes('upload')) {
      return <Zap className="w-4 h-4" />;
    }
    if (stepName?.toLowerCase().includes('agent')) {
      return <Loader2 className="w-4 h-4" />;
    }
    if (stepName?.toLowerCase().includes('cluster')) {
      return <CheckCircle className="w-4 h-4" />;
    }
    return <Clock className="w-4 h-4" />;
  };

  const getStepColor = (stepName) => {
    if (stepName?.toLowerCase().includes('complete')) {
      return 'text-success-600';
    }
    if (stepName?.toLowerCase().includes('error')) {
      return 'text-error-600';
    }
    return 'text-primary-600';
  };

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm w-full">
      <div className={`card shadow-lg border-l-4 ${
        type === 'success' ? 'border-l-success-500' :
        type === 'error' ? 'border-l-error-500' :
        'border-l-primary-500'
      }`}>
        <div className="card-content p-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              {getIcon()}
            </div>
            
            <div className="flex-1 min-w-0">
              <h4 className="font-medium text-gray-900 mb-1">
                {getTitle()}
              </h4>
              
              {step && (
                <div className="flex items-center space-x-2 mb-3">
                  {getStepIcon(step)}
                  <span className={`text-sm font-medium ${getStepColor(step)}`}>
                    {step}
                  </span>
                </div>
              )}
              
              {type === 'processing' && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>Progress</span>
                    <span>{Math.round(progress)}%</span>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}
              
              {type === 'success' && (
                <p className="text-sm text-gray-600">
                  Your accessibility analysis has been completed successfully.
                </p>
              )}
              
              {type === 'error' && (
                <p className="text-sm text-gray-600">
                  There was an error during analysis. Please try again.
                </p>
              )}
            </div>
            
            {onClose && (
              <button
                onClick={onClose}
                className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressToast;
