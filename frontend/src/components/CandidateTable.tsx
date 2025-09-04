import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronRight, FileText, MapPin, Tag } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import CodeSpan from '@/components/CodeSpan';
import { cn } from '@/lib/utils';

interface CandidateIssue {
  id: string;
  rule_id: string;
  title: string;
  description: string;
  evidence: Array<{
    file_path: string;
    start_line: number;
    end_line: number;
    code_snippet: string;
  }>;
  tags: string[];
  llm_model: string;
  confidence: 'low' | 'medium' | 'high';
}

interface CandidateTableProps {
  candidates: CandidateIssue[];
}

const CandidateTable: React.FC<CandidateTableProps> = ({ candidates }) => {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const toggleRow = (id: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedRows(newExpanded);
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getFileIcon = (filePath: string) => {
    const extension = filePath.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'html':
      case 'htm':
        return '🌐';
      case 'css':
        return '🎨';
      case 'js':
      case 'jsx':
      case 'ts':
      case 'tsx':
        return '⚡';
      case 'qml':
        return '📱';
      case 'xml':
        return '📄';
      default:
        return '📁';
    }
  };

  if (candidates.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-600 mb-2">No Issues Found</h3>
          <p className="text-gray-500">
            Great! No accessibility issues were discovered in your code.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Discovered Issues ({candidates.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {candidates.map((candidate, index) => (
            <motion.div
              key={candidate.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="border rounded-lg overflow-hidden"
            >
              <div
                className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => toggleRow(candidate.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {expandedRows.has(candidate.id) ? (
                      <ChevronDown className="h-4 w-4 text-gray-500" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-gray-500" />
                    )}
                    
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono text-xs">
                        {candidate.rule_id}
                      </Badge>
                      <h3 className="font-semibold text-gray-900">{candidate.title}</h3>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Badge className={cn("text-xs", getConfidenceColor(candidate.confidence))}>
                      {candidate.confidence}
                    </Badge>
                    <span className="text-sm text-gray-500">
                      {candidate.evidence.length} evidence
                    </span>
                  </div>
                </div>
                
                <p className="text-sm text-gray-600 mt-2 ml-7">
                  {candidate.description}
                </p>
              </div>
              
              {expandedRows.has(candidate.id) && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="border-t bg-gray-50 p-4"
                >
                  <div className="space-y-4">
                    {/* Evidence */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                        <MapPin className="h-4 w-4" />
                        Evidence ({candidate.evidence.length})
                      </h4>
                      <div className="space-y-3">
                        {candidate.evidence.map((evidence, evidenceIndex) => (
                          <div key={evidenceIndex} className="bg-white rounded border p-3">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-lg">{getFileIcon(evidence.file_path)}</span>
                              <span className="font-medium text-sm">{evidence.file_path}</span>
                              <Badge variant="outline" className="text-xs">
                                Lines {evidence.start_line}-{evidence.end_line}
                              </Badge>
                            </div>
                            <CodeSpan
                              code={evidence.code_snippet}
                              language={evidence.file_path.split('.').pop() || 'text'}
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {/* Tags */}
                    {candidate.tags.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                          <Tag className="h-4 w-4" />
                          Tags
                        </h4>
                        <div className="flex flex-wrap gap-1">
                          {candidate.tags.map((tag, tagIndex) => (
                            <Badge key={tagIndex} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Model Info */}
                    <div className="text-xs text-gray-500 pt-2 border-t">
                      Discovered by: <span className="font-mono">{candidate.llm_model}</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default CandidateTable;
