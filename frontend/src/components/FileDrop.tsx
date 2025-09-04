import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FileDropProps {
  onFilesSelected: (files: File[]) => void;
  maxFiles?: number;
  maxSize?: number; // in bytes
  acceptedTypes?: string[];
}

const FileDrop: React.FC<FileDropProps> = ({
  onFilesSelected,
  maxFiles = 20,
  maxSize = 10 * 1024 * 1024, // 10MB
  acceptedTypes = [
    'text/html',
    'text/css',
    'text/javascript',
    'application/javascript',
    'text/typescript',
    'application/typescript',
    'text/xml',
    'application/xml',
    'text/plain',
    'application/json'
  ]
}) => {
  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    if (rejectedFiles.length > 0) {
      console.warn('Some files were rejected:', rejectedFiles);
    }
    onFilesSelected(acceptedFiles);
  }, [onFilesSelected]);

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject,
    fileRejections
  } = useDropzone({
    onDrop,
    accept: acceptedTypes.reduce((acc, type) => {
      acc[type] = [];
      return acc;
    }, {} as Record<string, string[]>),
    maxFiles,
    maxSize,
    multiple: true
  });

  const getDropzoneContent = () => {
    if (isDragReject) {
      return (
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-lg font-semibold text-red-600 mb-2">
            Invalid file type
          </p>
          <p className="text-sm text-red-500">
            Please select supported file types (HTML, CSS, JS, TS, QML, XML)
          </p>
        </div>
      );
    }

    if (isDragActive) {
      return (
        <div className="text-center">
          <Upload className="h-12 w-12 text-blue-500 mx-auto mb-4 animate-bounce" />
          <p className="text-lg font-semibold text-blue-600 mb-2">
            Drop files here
          </p>
          <p className="text-sm text-blue-500">
            Release to upload your files
          </p>
        </div>
      );
    }

    return (
      <div className="text-center">
        <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-lg font-semibold text-gray-600 mb-2">
          Drag & drop files here
        </p>
        <p className="text-sm text-gray-500 mb-4">
          or click to browse
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {['HTML', 'CSS', 'JS', 'TS', 'QML', 'XML'].map((type) => (
            <span
              key={type}
              className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
            >
              {type}
            </span>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="w-full">
      <motion.div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-lg p-8 cursor-pointer transition-colors",
          "hover:border-blue-400 hover:bg-blue-50",
          isDragActive && !isDragReject && "border-blue-400 bg-blue-50",
          isDragReject && "border-red-400 bg-red-50"
        )}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <input {...getInputProps()} />
        {getDropzoneContent()}
      </motion.div>

      {fileRejections.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg"
        >
          <div className="flex items-center gap-2 text-red-600 mb-2">
            <AlertCircle className="h-4 w-4" />
            <span className="font-medium">Some files were rejected:</span>
          </div>
          <ul className="text-sm text-red-600 space-y-1">
            {fileRejections.map(({ file, errors }) => (
              <li key={file.name}>
                <strong>{file.name}:</strong> {errors.map(e => e.message).join(', ')}
              </li>
            ))}
          </ul>
        </motion.div>
      )}

      <div className="mt-4 text-xs text-gray-500 text-center">
        <p>Maximum {maxFiles} files, {Math.round(maxSize / 1024 / 1024)}MB each</p>
        <p>Supported: HTML, CSS, JavaScript, TypeScript, QML, XML</p>
      </div>
    </div>
  );
};

export default FileDrop;
