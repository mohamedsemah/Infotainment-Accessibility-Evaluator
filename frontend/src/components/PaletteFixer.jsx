import React, { useState, useEffect } from 'react';
import { 
  Palette, 
  RefreshCw, 
  Check, 
  X, 
  Download,
  Eye,
  Contrast,
  Droplets
} from 'lucide-react';

const PaletteFixer = ({ 
  contrastIssues, 
  onApplyFix, 
  onRejectFix 
}) => {
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [suggestedColors, setSuggestedColors] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (contrastIssues && contrastIssues.length > 0) {
      setSelectedIssue(contrastIssues[0]);
    }
  }, [contrastIssues]);

  useEffect(() => {
    if (selectedIssue) {
      generateColorSuggestions(selectedIssue);
    }
  }, [selectedIssue]);

  const generateColorSuggestions = async (issue) => {
    setIsGenerating(true);
    
    try {
      // Simulate API call to generate color suggestions
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const suggestions = generateColorPalette(issue);
      setSuggestedColors(suggestions);
    } catch (error) {
      console.error('Failed to generate color suggestions:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const generateColorPalette = (issue) => {
    // This would typically call an API to generate color suggestions
    // For now, we'll generate some mock suggestions
    const baseColor = issue.foreground_color || '#000000';
    const backgroundColor = issue.background_color || '#ffffff';
    
    return [
      {
        id: 1,
        foreground: '#000000',
        background: '#ffffff',
        contrast: 21,
        description: 'High contrast black on white'
      },
      {
        id: 2,
        foreground: '#1a1a1a',
        background: '#f5f5f5',
        contrast: 16.5,
        description: 'Dark gray on light gray'
      },
      {
        id: 3,
        foreground: '#2d3748',
        background: '#edf2f7',
        contrast: 12.6,
        description: 'Blue-gray on light blue-gray'
      },
      {
        id: 4,
        foreground: '#4a5568',
        background: '#e2e8f0',
        contrast: 9.2,
        description: 'Medium gray on light gray'
      }
    ];
  };

  const handleColorSelect = (suggestion) => {
    setSelectedIssue(prev => ({
      ...prev,
      suggested_foreground: suggestion.foreground,
      suggested_background: suggestion.background,
      suggested_contrast: suggestion.contrast
    }));
  };

  const handleApplyFix = () => {
    if (selectedIssue && selectedIssue.suggested_foreground) {
      onApplyFix(selectedIssue);
    }
  };

  const handleRejectFix = () => {
    onRejectFix(selectedIssue);
  };

  const getContrastLevel = (contrast) => {
    if (contrast >= 7) return { level: 'AAA', color: 'text-success-600' };
    if (contrast >= 4.5) return { level: 'AA', color: 'text-warning-600' };
    return { level: 'Fail', color: 'text-error-600' };
  };

  const ColorSwatch = ({ color, label, size = 'w-8 h-8' }) => (
    <div className="flex items-center space-x-2">
      <div 
        className={`${size} rounded border border-gray-300`}
        style={{ backgroundColor: color }}
      />
      <span className="text-sm text-gray-600">{label}</span>
    </div>
  );

  if (!contrastIssues || contrastIssues.length === 0) {
    return (
      <div className="card">
        <div className="card-content p-8 text-center">
          <Check className="w-12 h-12 text-success-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No Contrast Issues Found
          </h3>
          <p className="text-gray-600">
            All text elements meet WCAG contrast requirements.
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
          <div className="flex items-center space-x-3">
            <Palette className="w-6 h-6 text-primary-600" />
            <div>
              <h3 className="card-title text-lg">Color Palette Fixer</h3>
              <p className="card-description">
                Fix contrast issues by selecting from suggested color combinations
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Issue Selection */}
      <div className="card">
        <div className="card-header">
          <h4 className="font-semibold text-gray-900">Select Issue to Fix</h4>
        </div>
        <div className="card-content">
          <div className="space-y-3">
            {contrastIssues.map((issue) => (
              <div
                key={issue.id}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  selectedIssue?.id === issue.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedIssue(issue)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <ColorSwatch color={issue.foreground_color} label="Text" />
                      <span className="text-gray-400">on</span>
                      <ColorSwatch color={issue.background_color} label="Background" />
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Contrast className="w-4 h-4 text-gray-500" />
                      <span className="text-sm font-medium text-gray-900">
                        {issue.contrast_ratio}:1
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        issue.contrast_ratio >= 7 ? 'bg-success-100 text-success-700' :
                        issue.contrast_ratio >= 4.5 ? 'bg-warning-100 text-warning-700' :
                        'bg-error-100 text-error-700'
                      }`}>
                        {getContrastLevel(issue.contrast_ratio).level}
                      </span>
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-500">
                    {issue.element || 'Unknown element'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Color Suggestions */}
      {selectedIssue && (
        <div className="card">
          <div className="card-header">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-gray-900">Suggested Color Combinations</h4>
              {isGenerating && (
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Generating suggestions...</span>
                </div>
              )}
            </div>
          </div>
          <div className="card-content">
            {isGenerating ? (
              <div className="text-center py-8">
                <RefreshCw className="w-8 h-8 text-primary-600 animate-spin mx-auto mb-4" />
                <p className="text-gray-600">Generating color suggestions...</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {suggestedColors.map((suggestion) => (
                  <div
                    key={suggestion.id}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedIssue.suggested_foreground === suggestion.foreground
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleColorSelect(suggestion)}
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <ColorSwatch color={suggestion.foreground} label="Text" />
                          <span className="text-gray-400">on</span>
                          <ColorSwatch color={suggestion.background} label="Background" />
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Contrast className="w-4 h-4 text-gray-500" />
                          <span className="text-sm font-medium text-gray-900">
                            {suggestion.contrast}:1
                          </span>
                          <span className={`text-xs px-2 py-1 rounded ${
                            suggestion.contrast >= 7 ? 'bg-success-100 text-success-700' :
                            suggestion.contrast >= 4.5 ? 'bg-warning-100 text-warning-700' :
                            'bg-error-100 text-error-700'
                          }`}>
                            {getContrastLevel(suggestion.contrast).level}
                          </span>
                        </div>
                      </div>
                      
                      <p className="text-sm text-gray-600">
                        {suggestion.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      {selectedIssue && selectedIssue.suggested_foreground && (
        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Selected:</span>
                  <ColorSwatch color={selectedIssue.suggested_foreground} label="Text" />
                  <span className="text-gray-400">on</span>
                  <ColorSwatch color={selectedIssue.suggested_background} label="Background" />
                </div>
                
                <div className="flex items-center space-x-2">
                  <Contrast className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-900">
                    {selectedIssue.suggested_contrast}:1
                  </span>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleRejectFix}
                  className="btn btn-outline"
                >
                  <X className="w-4 h-4 mr-2" />
                  Reject
                </button>
                <button
                  onClick={handleApplyFix}
                  className="btn btn-primary"
                >
                  <Check className="w-4 h-4 mr-2" />
                  Apply Fix
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PaletteFixer;
