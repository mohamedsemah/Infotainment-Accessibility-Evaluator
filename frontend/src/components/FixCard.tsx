import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Wrench, ChevronDown, ChevronRight, AlertTriangle, CheckCircle, Copy, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import DiffViewer from '@/components/DiffViewer';
import { cn } from '@/lib/utils';

interface FixSuggestion {
  candidate_id: string;
  rule_id: string;
  patch_unified_diff: string;
  summary: string;
  side_effects: string[];
  test_suggestions: string[];
  llm_model: string;
}

interface FixCardProps {
  fix: FixSuggestion;
}

const FixCard: React.FC<FixCardProps> = ({ fix }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showDiff, setShowDiff] = useState(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getRuleIcon = (ruleId: string) => {
    switch (ruleId) {
      case '1.1.1':
        return '🖼️';
      case '1.4.3':
        return '🎨';
      case '2.5.5':
        return '👆';
      case '2.1.1':
        return '⌨️';
      case '2.4.7':
        return '🎯';
      default:
        return '🔧';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="border rounded-lg overflow-hidden"
    >
      <Card>
        <CardHeader
          className="cursor-pointer hover:bg-gray-50 transition-colors"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronRight className="h-4 w-4 text-gray-500" />
              )}
              
              <div className="flex items-center gap-2">
                <span className="text-lg">{getRuleIcon(fix.rule_id)}</span>
                <Wrench className="h-4 w-4 text-blue-600" />
                <h3 className="font-semibold text-gray-900">{fix.summary}</h3>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                {fix.rule_id}
              </Badge>
              <Badge variant="secondary" className="text-xs">
                {fix.candidate_id}
              </Badge>
            </div>
          </div>
        </CardHeader>
        
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <CardContent className="space-y-4">
              {/* Side Effects */}
              {fix.side_effects.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-orange-500" />
                    Potential Side Effects
                  </h4>
                  <ul className="space-y-1">
                    {fix.side_effects.map((effect, index) => (
                      <li key={index} className="text-sm text-orange-700 bg-orange-50 p-2 rounded border-l-4 border-orange-300">
                        {effect}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Test Suggestions */}
              {fix.test_suggestions.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    Test Suggestions
                  </h4>
                  <ul className="space-y-1">
                    {fix.test_suggestions.map((suggestion, index) => (
                      <li key={index} className="text-sm text-green-700 bg-green-50 p-2 rounded border-l-4 border-green-300">
                        {suggestion}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Patch Actions */}
              <div className="flex gap-2 pt-4 border-t">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowDiff(!showDiff)}
                >
                  {showDiff ? 'Hide' : 'Show'} Diff
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => copyToClipboard(fix.patch_unified_diff)}
                >
                  <Copy className="h-4 w-4 mr-2" />
                  Copy Patch
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    // In a real implementation, this would apply the patch
                    console.log('Apply patch:', fix.patch_unified_diff);
                  }}
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Apply Patch
                </Button>
              </div>
              
              {/* Diff Viewer */}
              {showDiff && fix.patch_unified_diff && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="pt-4"
                >
                  <h4 className="font-medium text-gray-900 mb-2">Unified Diff</h4>
                  <DiffViewer diff={fix.patch_unified_diff} />
                </motion.div>
              )}
              
              {/* Model Info */}
              <div className="text-xs text-gray-500 pt-2 border-t">
                Generated by: <span className="font-mono">{fix.llm_model}</span>
              </div>
            </CardContent>
          </motion.div>
        )}
      </Card>
    </motion.div>
  );
};

export default FixCard;
