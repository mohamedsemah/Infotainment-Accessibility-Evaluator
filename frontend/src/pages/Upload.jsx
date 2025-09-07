import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import useAppStore from '../store/useAppStore';
import apiClient from '../api/client';

const UploadPage = () => {
  const {
    uploadStatus,
    uploadProgress,
    uploadError,
    setUploadStatus,
    setUploadProgress,
    setUploadError,
    setUploadId,
    setCurrentPage
  } = useAppStore();

  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    // Validate file type
    const allowedTypes = [
      'application/zip',
      'application/x-zip-compressed',
      'application/octet-stream'
    ];
    
    if (!allowedTypes.includes(file.type) && !file.name.endsWith('.zip')) {
      setUploadError('Please upload a ZIP file containing your infotainment UI code');
      return;
    }

    // Validate file size (50MB max)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      setUploadError('File size must be less than 50MB');
      return;
    }

    setUploadStatus('uploading');
    setUploadError(null);
    setUploadProgress(0);

    try {
      const result = await apiClient.uploadZip(file, (progress) => {
        setUploadProgress(progress);
      });

      setUploadId(result.upload_id);
      setUploadStatus('success');
      setUploadProgress(100);
      
      // Navigate to results page after successful upload
      setTimeout(() => {
        setCurrentPage('results');
      }, 1500);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError(error.message || error.toString() || 'Upload failed');
      setUploadStatus('error');
    }
  }, [setUploadStatus, setUploadProgress, setUploadError, setUploadId, setCurrentPage]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/zip': ['.zip'],
      'application/x-zip-compressed': ['.zip']
    },
    maxFiles: 1,
    disabled: uploadStatus === 'uploading'
  });

  const handleRetry = () => {
    setUploadStatus('idle');
    setUploadError(null);
    setUploadProgress(0);
  };

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case 'uploading':
        return <Loader2 className="w-8 h-8 animate-spin text-primary-600" />;
      case 'success':
        return <CheckCircle className="w-8 h-8 text-success-600" />;
      case 'error':
        return <AlertCircle className="w-8 h-8 text-error-600" />;
      default:
        return <Upload className="w-8 h-8 text-gray-400" />;
    }
  };

  const getStatusMessage = () => {
    switch (uploadStatus) {
      case 'uploading':
        return `Uploading... ${Math.round(uploadProgress)}%`;
      case 'success':
        return 'Upload successful! Analyzing your code...';
      case 'error':
        return uploadError || 'Upload failed';
      default:
        return 'Drag and drop your ZIP file here, or click to browse';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Infotainment Accessibility Evaluator
          </h1>
          <p className="text-lg text-gray-600 max-w-xl mx-auto">
            Upload your infotainment UI code to get comprehensive accessibility analysis
            and automated fixes for WCAG 2.2 compliance.
          </p>
        </div>

        <div className="card">
          <div className="card-content">
            <div
              {...getRootProps()}
              className={`
                relative border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all duration-200
                ${isDragActive || dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300'}
                ${uploadStatus === 'uploading' ? 'pointer-events-none opacity-75' : ''}
                ${uploadStatus === 'success' ? 'border-success-500 bg-success-50' : ''}
                ${uploadStatus === 'error' ? 'border-error-500 bg-error-50' : ''}
                hover:border-primary-400 hover:bg-gray-50
              `}
              onDragEnter={() => setDragActive(true)}
              onDragLeave={() => setDragActive(false)}
            >
              <input {...getInputProps()} />
              
              <div className="flex flex-col items-center space-y-4">
                {getStatusIcon()}
                
                <div className="space-y-2">
                  <p className={`text-lg font-medium ${
                    uploadStatus === 'success' ? 'text-success-700' :
                    uploadStatus === 'error' ? 'text-error-700' :
                    'text-gray-700'
                  }`}>
                    {getStatusMessage()}
                  </p>
                  
                  {uploadStatus === 'uploading' && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  )}
                  
                  {uploadStatus === 'idle' && (
                    <p className="text-sm text-gray-500">
                      Supports HTML, QML, XML, CSS, JavaScript, and image files
                    </p>
                  )}
                </div>
              </div>
            </div>

            {uploadStatus === 'error' && (
              <div className="mt-6 flex justify-center">
                <button
                  onClick={handleRetry}
                  className="btn btn-outline"
                >
                  Try Again
                </button>
              </div>
            )}

            {uploadStatus === 'success' && (
              <div className="mt-6 text-center">
                <p className="text-sm text-gray-600">
                  Your code is being analyzed. This may take a few minutes...
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <FileText className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Comprehensive Analysis</h3>
            <p className="text-sm text-gray-600">
              Multi-agent system checks contrast, seizure safety, ARIA, language, and more
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <CheckCircle className="w-6 h-6 text-success-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Automated Fixes</h3>
            <p className="text-sm text-gray-600">
              Get suggested patches and apply them automatically in a sandbox environment
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <AlertCircle className="w-6 h-6 text-warning-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">WCAG 2.2 Compliance</h3>
            <p className="text-sm text-gray-600">
              Ensure your infotainment UI meets the latest accessibility standards
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
