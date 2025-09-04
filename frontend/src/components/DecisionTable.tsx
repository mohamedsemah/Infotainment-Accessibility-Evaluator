import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronRight, Gavel, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface ValidationDecision {
  candidate_id: string;
  rule_id: string;
  passed: boolean;
  severity: 'info' | 'minor' | 'moderate' | 'serious' | 'critical';
  reasoning: string;
  metrics_used: Record<string, any>;
  llm_model: string;
}

interface DecisionTableProps {
  decisions: ValidationDecision[];
}

const DecisionTable: React.FC<DecisionTableProps> = ({ decisions }) => {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const toggleRow = (candidateId: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(candidateId)) {
      newExpanded.delete(candidateId);
    } else {
      newExpanded.add(candidateId);
    }
    setExpandedRows(newExpanded);
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'serious':
        return <AlertTriangle className="h-4 w-4 text-orange-600" />;
      case 'moderate':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'minor':
        return <AlertTriangle className="h-4 w-4 text-blue-600" />;
      case 'info':
        return <AlertTriangle className="h-4 w-4 text-gray-600" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'serious':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'moderate':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'minor':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'info':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPassedIcon = (passed: boolean) => {
    return passed ? (
      <CheckCircle className="h-5 w-5 text-green-600" />
    ) : (
      <XCircle className="h-5 w-5 text-red-600" />
    );
  };

  const getPassedColor = (passed: boolean) => {
    return passed ? 'bg-green-100 text-green-800 border-green-200' : 'bg-red-100 text-red-800 border-red-200';
  };

  const formatMetricsUsed = (metrics: Record<string, any>) => {
    if (!metrics || Object.keys(metrics).length === 0) {
      return <span className="text-gray-500 italic">No metrics used</span>;
    }

    return (
      <div className="space-y-1">
        {Object.entries(metrics).map(([key, value]) => (
          <div key={key} className="flex items-center gap-2">
            <span className="font-mono text-sm">{key}:</span>
            <span className="font-medium">
              {typeof value === 'number' ? value.toFixed(2) : String(value)}
            </span>
          </div>
        ))}
      </div>
    );
  };

  const getStats = () => {
    const passed = decisions.filter(d => d.passed).length;
    const failed = decisions.filter(d => !d.passed).length;
    const bySeverity = decisions
      .filter(d => !d.passed)
      .reduce((acc, d) => {
        acc[d.severity] = (acc[d.severity] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

    return { passed, failed, bySeverity };
  };

  const stats = getStats();

  if (decisions.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <Gavel className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-600 mb-2">No Validation Decisions</h3>
          <p className="text-gray-500">
            No validation decisions were made for the discovered issues.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Gavel className="h-5 w-5" />
          Validation Decisions ({decisions.length})
        </CardTitle>
        <div className="flex gap-4 text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <span className="text-green-600 font-medium">{stats.passed} Passed</span>
          </div>
          <div className="flex items-center gap-2">
            <XCircle className="h-4 w-4 text-red-600" />
            <span className="text-red-600 font-medium">{stats.failed} Failed</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {decisions.map((decision, index) => {
            const isExpanded = expandedRows.has(decision.candidate_id);
            
            return (
              <motion.div
                key={decision.candidate_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border rounded-lg overflow-hidden"
              >
                <div
                  className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => toggleRow(decision.candidate_id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-gray-500" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-gray-500" />
                      )}
                      
                      <div className="flex items-center gap-2">
                        {getPassedIcon(decision.passed)}
                        <h3 className="font-semibold text-gray-900">
                          Rule {decision.rule_id}
                        </h3>
                        <Badge variant="outline" className="text-xs">
                          {decision.candidate_id}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Badge className={cn("text-xs", getPassedColor(decision.passed))}>
                        {decision.passed ? 'PASSED' : 'FAILED'}
                      </Badge>
                      {!decision.passed && (
                        <Badge className={cn("text-xs", getSeverityColor(decision.severity))}>
                          {getSeverityIcon(decision.severity)}
                          <span className="ml-1 capitalize">{decision.severity}</span>
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mt-2 ml-7">
                    {decision.reasoning}
                  </p>
                </div>
                
                {isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="border-t bg-gray-50 p-4"
                  >
                    <div className="space-y-4">
                      {/* Reasoning */}
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Detailed Reasoning</h4>
                        <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                          {decision.reasoning}
                        </p>
                      </div>
                      
                      {/* Metrics Used */}
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Metrics Used</h4>
                        <div className="bg-white p-3 rounded border">
                          {formatMetricsUsed(decision.metrics_used)}
                        </div>
                      </div>
                      
                      {/* Model Info */}
                      <div className="text-xs text-gray-500 pt-2 border-t">
                        Validated by: <span className="font-mono">{decision.llm_model}</span>
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

export default DecisionTable;
