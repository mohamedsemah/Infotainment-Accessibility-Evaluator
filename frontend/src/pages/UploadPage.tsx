import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Upload, FileText, Play, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import FileDrop from '@/components/FileDrop';
import ModelMapSelector from '@/components/ModelMapSelector';
import { api } from '@/api/client';
import { useToast } from '@/hooks/use-toast';

const UploadPage: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleFilesSelected = (selectedFiles: File[]) => {
    setFiles(selectedFiles);
  };

  const handleRunPipeline = async () => {
    if (files.length === 0) {
      toast({
        title: "No files selected",
        description: "Please select at least one file to analyze.",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    try {
      // Upload files
      const uploadResponse = await api.uploadFiles(files);
      const sessionId = uploadResponse.data.session_id;

      // Run pipeline
      setIsRunning(true);
      const pipelineResponse = await api.runPipeline({
        session_id: sessionId,
        model_map: {
          llm1: "claude-opus-4-1-20250805",
          llm2: "deepseek-chat",
          llm3: "grok-4",
          llm4: "gpt-5"
        },
        files: files.map(file => ({
          path: file.name,
          content: "" // Content will be read from uploaded files
        }))
      });

      // Navigate to results page
      navigate(`/results/${sessionId}`);
      
      toast({
        title: "Pipeline completed",
        description: `Found ${pipelineResponse.data.candidates.length} accessibility issues.`,
      });

    } catch (error: any) {
      console.error('Pipeline execution failed:', error);
      toast({
        title: "Pipeline failed",
        description: error.response?.data?.detail || "An error occurred while running the pipeline.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      setIsRunning(false);
    }
  };

  const getFileTypeIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Infotainment Accessibility Evaluator
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Analyze your infotainment UI code for WCAG 2.2 compliance using our 4-stage LLM pipeline
          </p>
        </motion.div>

        {/* Pipeline Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mb-8"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                4-Stage Pipeline
              </CardTitle>
              <CardDescription>
                Our advanced pipeline uses multiple LLMs to ensure comprehensive accessibility analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">1</div>
                  <div className="font-semibold text-blue-800">Discovery</div>
                  <div className="text-sm text-blue-600">Claude Opus 4.1</div>
                  <div className="text-xs text-gray-600 mt-1">Find potential issues</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">2</div>
                  <div className="font-semibold text-green-800">Metrics</div>
                  <div className="text-sm text-green-600">DeepSeek V3</div>
                  <div className="text-xs text-gray-600 mt-1">Compute measurements</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">3</div>
                  <div className="font-semibold text-orange-800">Validation</div>
                  <div className="text-sm text-orange-600">Grok-4</div>
                  <div className="text-xs text-gray-600 mt-1">Pass/fail decisions</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">4</div>
                  <div className="font-semibold text-purple-800">Fixes</div>
                  <div className="text-sm text-purple-600">GPT-5</div>
                  <div className="text-xs text-gray-600 mt-1">Generate patches</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* File Upload */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="lg:col-span-2"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Upload Files
                </CardTitle>
                <CardDescription>
                  Drag and drop your infotainment UI files (HTML, CSS, JS, QML, XML, etc.)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileDrop onFilesSelected={handleFilesSelected} />
                
                {files.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    transition={{ duration: 0.3 }}
                    className="mt-6"
                  >
                    <h3 className="font-semibold mb-3">Selected Files ({files.length})</h3>
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {files.map((file, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.2, delay: index * 0.1 }}
                          className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
                        >
                          <span className="text-2xl">{getFileTypeIcon(file.name)}</span>
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-sm truncate">{file.name}</div>
                            <div className="text-xs text-gray-500">
                              {(file.size / 1024).toFixed(1)} KB
                            </div>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {file.name.split('.').pop()?.toUpperCase()}
                          </Badge>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Configuration & Actions */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="space-y-6"
          >
            {/* Model Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Configuration
                </CardTitle>
                <CardDescription>
                  Premium model configuration
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ModelMapSelector />
              </CardContent>
            </Card>

            {/* Run Pipeline */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Play className="h-5 w-5" />
                  Run Analysis
                </CardTitle>
                <CardDescription>
                  Execute the 4-stage accessibility pipeline
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={handleRunPipeline}
                  disabled={files.length === 0 || isUploading || isRunning}
                  className="w-full"
                  size="lg"
                >
                  {isUploading ? (
                    <>
                      <Upload className="h-4 w-4 mr-2 animate-spin" />
                      Uploading Files...
                    </>
                  ) : isRunning ? (
                    <>
                      <Play className="h-4 w-4 mr-2 animate-pulse" />
                      Running Pipeline...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Run Premium Pipeline
                    </>
                  )}
                </Button>
                
                {files.length > 0 && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <div className="text-sm text-blue-800">
                      <strong>Ready to analyze:</strong> {files.length} file{files.length !== 1 ? 's' : ''}
                    </div>
                    <div className="text-xs text-blue-600 mt-1">
                      Estimated time: {Math.ceil(files.length * 0.5)}-{Math.ceil(files.length * 1.5)} minutes
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Supported Formats */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Supported Formats
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex flex-wrap gap-1">
                    {['HTML', 'CSS', 'JS', 'TS', 'JSX', 'TSX', 'QML', 'XML'].map((format) => (
                      <Badge key={format} variant="secondary" className="text-xs">
                        {format}
                      </Badge>
                    ))}
                  </div>
                  <p className="text-xs text-gray-600 mt-2">
                    We support most web and infotainment UI formats. Files are analyzed for WCAG 2.2 compliance.
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
