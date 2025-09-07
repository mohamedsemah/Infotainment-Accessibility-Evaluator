import React from 'react';
import { X, Filter } from 'lucide-react';

const Filters = ({ filters, onFilterChange }) => {
  const severityOptions = [
    { value: 'all', label: 'All Severities', count: null },
    { value: 'critical', label: 'Critical', count: null },
    { value: 'high', label: 'High', count: null },
    { value: 'medium', label: 'Medium', count: null },
    { value: 'low', label: 'Low', count: null }
  ];

  const confidenceOptions = [
    { value: 'all', label: 'All Confidence Levels', count: null },
    { value: 'high', label: 'High Confidence', count: null },
    { value: 'medium', label: 'Medium Confidence', count: null },
    { value: 'low', label: 'Low Confidence', count: null }
  ];

  const agentOptions = [
    { value: 'all', label: 'All Agents', count: null },
    { value: 'contrast', label: 'Contrast Agent', count: null },
    { value: 'seizure_safe', label: 'Seizure Safe Agent', count: null },
    { value: 'language', label: 'Language Agent', count: null },
    { value: 'aria', label: 'ARIA Agent', count: null },
    { value: 'state_explorer', label: 'State Explorer Agent', count: null },
    { value: 'triage', label: 'Triage Agent', count: null },
    { value: 'token_harmonizer', label: 'Token Harmonizer Agent', count: null }
  ];

  const statusOptions = [
    { value: 'all', label: 'All Statuses', count: null },
    { value: 'open', label: 'Open', count: null },
    { value: 'fixed', label: 'Fixed', count: null },
    { value: 'ignored', label: 'Ignored', count: null }
  ];

  const handleFilterChange = (key, value) => {
    onFilterChange({ [key]: value });
  };

  const handleClearAll = () => {
    onFilterChange({
      severity: 'all',
      confidence: 'all',
      agent: 'all',
      status: 'all',
      search: ''
    });
  };

  const hasActiveFilters = Object.entries(filters).some(([key, value]) => 
    value !== 'all' && value !== ''
  );

  const FilterSection = ({ title, options, value, onChange }) => (
    <div className="space-y-2">
      <h4 className="font-medium text-gray-900 text-sm">{title}</h4>
      <div className="space-y-1">
        {options.map((option) => (
          <label key={option.value} className="flex items-center space-x-2 cursor-pointer">
            <input
              type="radio"
              name={title.toLowerCase().replace(' ', '-')}
              value={option.value}
              checked={value === option.value}
              onChange={(e) => onChange(e.target.value)}
              className="w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700 flex-1">
              {option.label}
            </span>
            {option.count !== null && (
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                {option.count}
              </span>
            )}
          </label>
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={handleClearAll}
            className="text-sm text-primary-600 hover:text-primary-700 flex items-center space-x-1"
          >
            <X className="w-4 h-4" />
            <span>Clear all</span>
          </button>
        )}
      </div>

      {/* Search */}
      <div className="space-y-2">
        <h4 className="font-medium text-gray-900 text-sm">Search</h4>
        <input
          type="text"
          placeholder="Search findings..."
          value={filters.search}
          onChange={(e) => handleFilterChange('search', e.target.value)}
          className="input w-full"
        />
      </div>

      {/* Severity Filter */}
      <FilterSection
        title="Severity"
        options={severityOptions}
        value={filters.severity}
        onChange={(value) => handleFilterChange('severity', value)}
      />

      {/* Confidence Filter */}
      <FilterSection
        title="Confidence"
        options={confidenceOptions}
        value={filters.confidence}
        onChange={(value) => handleFilterChange('confidence', value)}
      />

      {/* Agent Filter */}
      <FilterSection
        title="Agent"
        options={agentOptions}
        value={filters.agent}
        onChange={(value) => handleFilterChange('agent', value)}
      />

      {/* Status Filter */}
      <FilterSection
        title="Status"
        options={statusOptions}
        value={filters.status}
        onChange={(value) => handleFilterChange('status', value)}
      />

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="pt-4 border-t border-gray-200">
          <h4 className="font-medium text-gray-900 text-sm mb-2">Active Filters</h4>
          <div className="flex flex-wrap gap-2">
            {filters.severity !== 'all' && (
              <span className="badge badge-sm badge-primary">
                Severity: {filters.severity}
              </span>
            )}
            {filters.confidence !== 'all' && (
              <span className="badge badge-sm badge-primary">
                Confidence: {filters.confidence}
              </span>
            )}
            {filters.agent !== 'all' && (
              <span className="badge badge-sm badge-primary">
                Agent: {filters.agent.replace('_', ' ')}
              </span>
            )}
            {filters.status !== 'all' && (
              <span className="badge badge-sm badge-primary">
                Status: {filters.status}
              </span>
            )}
            {filters.search && (
              <span className="badge badge-sm badge-primary">
                Search: "{filters.search}"
              </span>
            )}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="pt-4 border-t border-gray-200">
        <h4 className="font-medium text-gray-900 text-sm mb-2">Quick Actions</h4>
        <div className="space-y-2">
          <button
            onClick={() => handleFilterChange('severity', 'critical')}
            className="w-full text-left text-sm text-error-600 hover:text-error-700 py-1"
          >
            Show only critical issues
          </button>
          <button
            onClick={() => handleFilterChange('confidence', 'high')}
            className="w-full text-left text-sm text-success-600 hover:text-success-700 py-1"
          >
            Show only high confidence findings
          </button>
          <button
            onClick={() => handleFilterChange('status', 'open')}
            className="w-full text-left text-sm text-primary-600 hover:text-primary-700 py-1"
          >
            Show only open issues
          </button>
        </div>
      </div>
    </div>
  );
};

export default Filters;
