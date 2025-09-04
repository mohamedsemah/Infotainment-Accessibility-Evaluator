import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronRight, BarChart3, AlertCircle, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface Metric {
  name: string;
  scope_id: string;
  value: number | string | boolean | null;
  unit?: string;
  computed_from: any[];
  notes?: string;
  llm_model: string;
}

interface MetricTableProps {
  metrics: Metric[];
}

const MetricTable: React.FC<MetricTableProps> = ({ metrics }) => {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const toggleRow = (scopeId: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(scopeId)) {
      newExpanded.delete(scopeId);
    } else {
      newExpanded.add(scopeId);
    }
    setExpandedRows(newExpanded);
  };

  const formatValue = (value: any, unit?: string) => {
    if (value === null || value === undefined) {
      return (
        <div className="flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-yellow-500" />
          <span className="text-yellow-600 font-medium">Not computed</span>
        </div>
      );
    }

    if (typeof value === 'boolean') {
      return (
        <div className="flex items-center gap-2">
          {value ? (
            <CheckCircle className="h-4 w-4 text-green-500" />
          ) : (
            <AlertCircle className="h-4 w-4 text-red-500" />
          )}
          <span className={cn(
            "font-medium",
            value ? "text-green-600" : "text-red-600"
          )}>
            {value ? 'Yes' : 'No'}
          </span>
        </div>
      );
    }

    if (typeof value === 'number') {
      const formattedValue = value.toFixed(2);
      return (
        <div className="flex items-center gap-2">
          <span className="font-mono font-medium">{formattedValue}</span>
          {unit && <span className="text-sm text-gray-500">{unit}</span>}
        </div>
      );
    }

    return (
      <span className="font-medium">{String(value)}</span>
    );
  };

  const getMetricIcon = (name: string) => {
    switch (name) {
      case 'contrast_ratio':
        return '🎨';
      case 'target_size_min_px':
        return '👆';
      case 'alt_text_present':
        return '🖼️';
      case 'keyboard_accessible':
        return '⌨️';
      case 'focus_indicator_visibility':
        return '🎯';
      case 'programmatic_structure':
        return '🏗️';
      default:
        return '📊';
    }
  };

  const getValueStatus = (metric: Metric) => {
    if (metric.value === null || metric.value === undefined) {
      return 'warning';
    }

    // Check against WCAG thresholds
    if (metric.name === 'contrast_ratio' && typeof metric.value === 'number') {
      if (metric.value >= 7.0) return 'excellent';
      if (metric.value >= 4.5) return 'good';
      if (metric.value >= 3.0) return 'warning';
      return 'error';
    }

    if (metric.name === 'target_size_min_px' && typeof metric.value === 'number') {
      if (metric.value >= 44) return 'good';
      return 'error';
    }

    if (typeof metric.value === 'boolean') {
      return metric.value ? 'good' : 'error';
    }

    return 'neutral';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'good':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (metrics.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-600 mb-2">No Metrics Computed</h3>
          <p className="text-gray-500">
            No metrics were computed for the discovered issues.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Computed Metrics ({metrics.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {metrics.map((metric, index) => {
            const status = getValueStatus(metric);
            const isExpanded = expandedRows.has(metric.scope_id);
            
            return (
              <motion.div
                key={metric.scope_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border rounded-lg overflow-hidden"
              >
                <div
                  className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => toggleRow(metric.scope_id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-gray-500" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-gray-500" />
                      )}
                      
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{getMetricIcon(metric.name)}</span>
                        <h3 className="font-semibold text-gray-900 capitalize">
                          {metric.name.replace(/_/g, ' ')}
                        </h3>
                        <Badge variant="outline" className="text-xs">
                          {metric.scope_id}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      {formatValue(metric.value, metric.unit)}
                      <Badge className={cn("text-xs", getStatusColor(status))}>
                        {status}
                      </Badge>
                    </div>
                  </div>
                </div>
                
                {isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="border-t bg-gray-50 p-4"
                  >
                    <div className="space-y-3">
                      {/* Notes */}
                      {metric.notes && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Notes</h4>
                          <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                            {metric.notes}
                          </p>
                        </div>
                      )}
                      
                      {/* Computed From */}
                      {metric.computed_from && metric.computed_from.length > 0 && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Computed From</h4>
                          <div className="space-y-2">
                            {metric.computed_from.map((source, sourceIndex) => (
                              <div key={sourceIndex} className="bg-white p-3 rounded border">
                                <div className="flex items-center gap-2">
                                  <span className="text-sm font-medium">{source.file_path}</span>
                                  <Badge variant="outline" className="text-xs">
                                    Lines {source.start_line}-{source.end_line}
                                  </Badge>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {/* Model Info */}
                      <div className="text-xs text-gray-500 pt-2 border-t">
                        Computed by: <span className="font-mono">{metric.llm_model}</span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default MetricTable;
