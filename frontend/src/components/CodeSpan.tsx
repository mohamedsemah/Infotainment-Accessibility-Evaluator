import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface CodeSpanProps {
  code: string;
  language?: string;
  showLineNumbers?: boolean;
  maxHeight?: string;
}

const CodeSpan: React.FC<CodeSpanProps> = ({
  code,
  language = 'text',
  showLineNumbers = false,
  maxHeight = '200px'
}) => {
  // Clean up the code
  const cleanCode = code.trim();
  
  // Determine language from common patterns if not specified
  const detectLanguage = (code: string, fallback: string) => {
    if (fallback !== 'text') return fallback;
    
    if (code.includes('<html') || code.includes('<!DOCTYPE')) return 'html';
    if (code.includes('{') && code.includes('}') && code.includes(':')) return 'css';
    if (code.includes('function') || code.includes('const') || code.includes('let')) return 'javascript';
    if (code.includes('import') && code.includes('from')) return 'typescript';
    if (code.includes('<?xml') || code.includes('<root>')) return 'xml';
    
    return 'text';
  };

  const detectedLanguage = detectLanguage(cleanCode, language);

  return (
    <div className="relative">
      <div 
        className="overflow-auto rounded border bg-gray-900"
        style={{ maxHeight }}
      >
        <SyntaxHighlighter
          language={detectedLanguage}
          style={tomorrow}
          showLineNumbers={showLineNumbers}
          customStyle={{
            margin: 0,
            padding: '1rem',
            fontSize: '0.875rem',
            lineHeight: '1.5',
            background: 'transparent'
          }}
          lineNumberStyle={{
            color: '#6b7280',
            marginRight: '1rem',
            userSelect: 'none'
          }}
        >
          {cleanCode}
        </SyntaxHighlighter>
      </div>
      
      {/* Copy button */}
      <button
        onClick={() => {
          navigator.clipboard.writeText(cleanCode);
        }}
        className="absolute top-2 right-2 p-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white rounded text-xs transition-colors"
        title="Copy code"
      >
        📋
      </button>
    </div>
  );
};

export default CodeSpan;
