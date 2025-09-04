import React from 'react';
import { motion } from 'framer-motion';

interface DiffViewerProps {
  diff: string;
  maxHeight?: string;
}

const DiffViewer: React.FC<DiffViewerProps> = ({ diff, maxHeight = '400px' }) => {
  const parseDiff = (diffText: string) => {
    const lines = diffText.split('\n');
    const parsedLines = lines.map((line, index) => {
      let type = 'context';
      let content = line;
      
      if (line.startsWith('---') || line.startsWith('+++')) {
        type = 'header';
      } else if (line.startsWith('@@')) {
        type = 'hunk-header';
      } else if (line.startsWith('+')) {
        type = 'added';
        content = line.substring(1);
      } else if (line.startsWith('-')) {
        type = 'removed';
        content = line.substring(1);
      } else if (line.startsWith(' ')) {
        type = 'context';
        content = line.substring(1);
      }
      
      return {
        lineNumber: index + 1,
        type,
        content,
        originalLine: line
      };
    });
    
    return parsedLines;
  };

  const getLineStyle = (type: string) => {
    switch (type) {
      case 'header':
        return 'bg-blue-50 text-blue-800 font-medium';
      case 'hunk-header':
        return 'bg-purple-50 text-purple-800 font-medium';
      case 'added':
        return 'bg-green-50 text-green-800 border-l-4 border-green-400';
      case 'removed':
        return 'bg-red-50 text-red-800 border-l-4 border-red-400';
      case 'context':
        return 'bg-gray-50 text-gray-800';
      default:
        return 'bg-white text-gray-800';
    }
  };

  const getLineIcon = (type: string) => {
    switch (type) {
      case 'added':
        return '+';
      case 'removed':
        return '-';
      case 'context':
        return ' ';
      default:
        return '';
    }
  };

  const parsedLines = parseDiff(diff);

  return (
    <div className="border rounded-lg overflow-hidden">
      <div 
        className="overflow-auto font-mono text-sm"
        style={{ maxHeight }}
      >
        {parsedLines.map((line, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.01 }}
            className={cn(
              "flex items-start px-4 py-1 border-b border-gray-200 last:border-b-0",
              getLineStyle(line.type)
            )}
          >
            <div className="flex-shrink-0 w-8 text-right pr-3 text-gray-500 select-none">
              {line.lineNumber}
            </div>
            <div className="flex-shrink-0 w-6 text-center pr-2 font-bold">
              {getLineIcon(line.type)}
            </div>
            <div className="flex-1 min-w-0">
              <span className="whitespace-pre-wrap break-words">
                {line.content}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
      
      {/* Legend */}
      <div className="bg-gray-100 px-4 py-2 border-t">
        <div className="flex items-center gap-4 text-xs text-gray-600">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-green-400 rounded"></div>
            <span>Added</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-red-400 rounded"></div>
            <span>Removed</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-gray-400 rounded"></div>
            <span>Context</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiffViewer;
