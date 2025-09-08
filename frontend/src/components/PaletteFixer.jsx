import React, { useState, useEffect } from 'react';
import { Palette, CheckCircle, XCircle, RotateCcw } from 'lucide-react';

const PaletteFixer = ({ contrastIssues, onApplyFix, onReset }) => {
  const [selectedIssues, setSelectedIssues] = useState(new Set());
  const [colorSuggestions, setColorSuggestions] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (contrastIssues.length > 0) {
      generateColorSuggestions();
    }
  }, [contrastIssues]);

  const generateColorSuggestions = async () => {
    setIsGenerating(true);
    
    // Simulate color suggestion generation
    // In a real implementation, this would call an API
    const suggestions = {};
    
    contrastIssues.forEach((issue, index) => {
      const currentRatio = issue.metrics?.ratio || 0;
      const requiredRatio = issue.metrics?.required_ratio || 4.5;
      
      if (currentRatio < requiredRatio) {
        // Generate color suggestions based on current colors
        const currentFg = issue.metrics?.foreground_color || '#000000';
        const currentBg = issue.metrics?.background_color || '#ffffff';
        
        suggestions[issue.id] = {
          original: {
            foreground: currentFg,
            background: currentBg,
            ratio: currentRatio
          },
          suggestions: [
            {
              foreground: adjustColorBrightness(currentFg, 0.2),
              background: currentBg,
              ratio: calculateContrastRatio(adjustColorBrightness(currentFg, 0.2), currentBg),
              description: 'Darker foreground'
            },
            {
              foreground: currentFg,
              background: adjustColorBrightness(currentBg, -0.2),
              ratio: calculateContrastRatio(currentFg, adjustColorBrightness(currentBg, -0.2)),
              description: 'Lighter background'
            },
            {
              foreground: '#ffffff',
              background: '#000000',
              ratio: 21,
              description: 'High contrast option'
            }
          ]
        };
      }
    });
    
    setColorSuggestions(suggestions);
    setIsGenerating(false);
  };

  const adjustColorBrightness = (hex, factor) => {
    // Simple color brightness adjustment
    const num = parseInt(hex.replace('#', ''), 16);
    const r = Math.max(0, Math.min(255, Math.floor((num >> 16) * (1 + factor))));
    const g = Math.max(0, Math.min(255, Math.floor(((num >> 8) & 0xFF) * (1 + factor))));
    const b = Math.max(0, Math.min(255, Math.floor((num & 0xFF) * (1 + factor))));
    return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
  };

  const calculateContrastRatio = (color1, color2) => {
    // Simplified contrast ratio calculation
    // In a real implementation, this would use proper WCAG contrast calculation
    const getLuminance = (hex) => {
      const rgb = parseInt(hex.replace('#', ''), 16);
      const r = (rgb >> 16) & 0xFF;
      const g = (rgb >> 8) & 0xFF;
      const b = rgb & 0xFF;
      return (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    };
    
    const lum1 = getLuminance(color1);
    const lum2 = getLuminance(color2);
    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);
    return (brightest + 0.05) / (darkest + 0.05);
  };

  const handleIssueSelect = (issueId) => {
    const newSelected = new Set(selectedIssues);
    if (newSelected.has(issueId)) {
      newSelected.delete(issueId);
    } else {
      newSelected.add(issueId);
    }
    setSelectedIssues(newSelected);
  };

  const handleSuggestionSelect = (issueId, suggestion) => {
    if (onApplyFix) {
      onApplyFix(issueId, suggestion);
    }
  };

  const handleSelectAll = () => {
    if (selectedIssues.size === contrastIssues.length) {
      setSelectedIssues(new Set());
    } else {
      setSelectedIssues(new Set(contrastIssues.map(issue => issue.id)));
    }
  };

  const handleReset = () => {
    setSelectedIssues(new Set());
    if (onReset) {
      onReset();
    }
  };

  const getRatioColor = (ratio, required) => {
    if (ratio >= required) return 'text-green-600';
    if (ratio >= required * 0.8) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRatioBackground = (ratio, required) => {
    if (ratio >= required) return 'bg-green-50 border-green-200';
    if (ratio >= required * 0.8) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  if (contrastIssues.length === 0) {
    return (
      <div className="text-center py-8">
        <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Contrast Issues</h3>
        <p className="text-gray-600">
          All color combinations meet WCAG contrast requirements.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Palette className="w-6 h-6 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900">Color Palette Fixer</h2>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleSelectAll}
            className="btn btn-outline btn-sm"
          >
            {selectedIssues.size === contrastIssues.length ? 'Deselect All' : 'Select All'}
          </button>
          <button
            onClick={handleReset}
            className="btn btn-outline btn-sm"
          >
            <RotateCcw className="w-4 h-4 mr-1" />
            Reset
          </button>
        </div>
      </div>

      {/* Issues List */}
      <div className="space-y-4">
        {contrastIssues.map((issue) => {
          const suggestions = colorSuggestions[issue.id];
          const isSelected = selectedIssues.has(issue.id);
          const currentRatio = issue.metrics?.ratio || 0;
          const requiredRatio = issue.metrics?.required_ratio || 4.5;

          return (
            <div
              key={issue.id}
              className={`border rounded-lg p-4 transition-all ${
                isSelected ? 'ring-2 ring-primary-500 border-primary-300' : 'border-gray-200'
              }`}
            >
              {/* Issue Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => handleIssueSelect(issue.id)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded mt-1"
                  />
                  <div>
                    <h3 className="font-medium text-gray-900">{issue.details}</h3>
                    <p className="text-sm text-gray-600">
                      {issue.file_path}:{issue.line_number}
                    </p>
                  </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${getRatioBackground(currentRatio, requiredRatio)}`}>
                  <span className={getRatioColor(currentRatio, requiredRatio)}>
                    {currentRatio.toFixed(1)}:1
                  </span>
                </div>
              </div>

              {/* Current Colors */}
              {suggestions && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Current Colors</h4>
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-8 h-8 rounded border"
                        style={{ backgroundColor: suggestions.original.foreground }}
                      />
                      <span className="text-sm text-gray-600">Foreground</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-8 h-8 rounded border"
                        style={{ backgroundColor: suggestions.original.background }}
                      />
                      <span className="text-sm text-gray-600">Background</span>
                    </div>
                    <div className="text-sm text-gray-600">
                      Ratio: <span className={getRatioColor(currentRatio, requiredRatio)}>
                        {currentRatio.toFixed(1)}:1
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Color Suggestions */}
              {suggestions && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Suggested Fixes</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {suggestions.suggestions.map((suggestion, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                          suggestion.ratio >= requiredRatio
                            ? 'border-green-200 bg-green-50'
                            : 'border-gray-200 bg-white'
                        }`}
                        onClick={() => handleSuggestionSelect(issue.id, suggestion)}
                      >
                        <div className="flex items-center space-x-3 mb-2">
                          <div
                            className="w-6 h-6 rounded border"
                            style={{ backgroundColor: suggestion.foreground }}
                          />
                          <div
                            className="w-6 h-6 rounded border"
                            style={{ backgroundColor: suggestion.background }}
                          />
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-900">
                              {suggestion.description}
                            </div>
                            <div className={`text-xs ${
                              suggestion.ratio >= requiredRatio ? 'text-green-600' : 'text-gray-600'
                            }`}>
                              {suggestion.ratio.toFixed(1)}:1
                            </div>
                          </div>
                        </div>
                        {suggestion.ratio >= requiredRatio && (
                          <div className="flex items-center text-green-600 text-xs">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Meets WCAG AA
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <div className="text-sm text-gray-600">
          {selectedIssues.size} of {contrastIssues.length} issues selected
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleReset}
            className="btn btn-outline"
          >
            Reset All
          </button>
          <button
            onClick={() => {
              // Apply all selected fixes
              selectedIssues.forEach(issueId => {
                const suggestions = colorSuggestions[issueId];
                if (suggestions && suggestions.suggestions.length > 0) {
                  handleSuggestionSelect(issueId, suggestions.suggestions[0]);
                }
              });
            }}
            disabled={selectedIssues.size === 0}
            className="btn btn-primary"
          >
            Apply Selected Fixes
          </button>
        </div>
      </div>
    </div>
  );
};

export default PaletteFixer;