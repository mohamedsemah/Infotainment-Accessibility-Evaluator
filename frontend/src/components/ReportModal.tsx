import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Download, FileText, Archive, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/api/client';
import { useToast } from '@/hooks/use-toast';

interface ReportModalProps {
  pipelineData: any;
  onClose: () => void;
}

const ReportModal: React.FC<ReportModalProps> = ({ pipelineData, onClose }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const { toast } = useToast();

  const handleExportPDF = async () => {
    setIsGenerating(true);
    try {
      const response = await api.generatePDFReport(pipelineData.session_id);
      
      // Create download link
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `accessibility-report-${pipelineData.session_id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "PDF Report Generated",
        description: "Your accessibility report has been downloaded.",
      });
    } catch (error: any) {
      toast({
        title: "Export Failed",
        description: error.response?.data?.detail || "Failed to generate PDF report.",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExportZIP = async () => {
    setIsGenerating(true);
    try {
      const response = await api.exportPatchedFiles(pipelineData.session_id);
      
      // Create download link
      const blob = new Blob([response.data], { type: 'application/zip' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `patched-files-${pipelineData.session_id}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "ZIP Archive Generated",
        description: "Your patched files have been downloaded.",
      });
    } catch (error: any) {
      toast({
        title: "Export Failed",
        description: error.response?.data?.detail || "Failed to generate ZIP archive.",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const getStats = () => {
    const decisions = pipelineData.decisions;
    const passed = decisions.filter((d: any) => d.passed).length;
    const failed = decisions.filter((d: any) => !d.passed).length;
    
    const bySeverity = failed > 0 ? decisions
      .filter((d: any) => !d.passed)
      .reduce((acc: any, d: any) => {
        acc[d.severity] = (acc[d.severity] || 0) + 1;
        return acc;
      }, {}) : {};
    
    return { passed, failed, bySeverity };
  };

  const stats = getStats();

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between p-6 border-b">
            <h2 className="text-xl font-semibold text-gray-900">Export Report</h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="p-6 space-y-6 overflow-y-auto max-h-[calc(90vh-120px)]">
            {/* Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Analysis Summary</CardTitle>
                <CardDescription>
                  Session: {pipelineData.session_id}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {pipelineData.candidates.length}
                    </div>
                    <div className="text-sm text-gray-600">Issues Found</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {stats.passed}
                    </div>
                    <div className="text-sm text-gray-600">Passed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {stats.failed}
                    </div>
                    <div className="text-sm text-gray-600">Failed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {pipelineData.fixes.length}
                    </div>
                    <div className="text-sm text-gray-600">Fixes</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Export Options */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Export Options</h3>
              
              {/* PDF Report */}
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-red-100 rounded-lg">
                        <FileText className="h-5 w-5 text-red-600" />
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">PDF Report</h4>
                        <p className="text-sm text-gray-600">
                          Comprehensive accessibility report with all findings
                        </p>
                      </div>
                    </div>
                    <Button
                      onClick={handleExportPDF}
                      disabled={isGenerating}
                      className="flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      {isGenerating ? 'Generating...' : 'Download PDF'}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* ZIP Archive */}
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <Archive className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">ZIP Archive</h4>
                        <p className="text-sm text-gray-600">
                          Patched files with applied accessibility fixes
                        </p>
                      </div>
                    </div>
                    <Button
                      onClick={handleExportZIP}
                      disabled={isGenerating}
                      variant="outline"
                      className="flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      {isGenerating ? 'Generating...' : 'Download ZIP'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Report Contents */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Report Contents</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-gray-500" />
                    <span className="text-sm text-gray-700">
                      Executive summary with key findings
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-gray-500" />
                    <span className="text-sm text-gray-700">
                      Detailed issue analysis with code snippets
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-gray-500" />
                    <span className="text-sm text-gray-700">
                      WCAG compliance metrics and thresholds
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-gray-500" />
                    <span className="text-sm text-gray-700">
                      Fix suggestions with unified diff patches
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-gray-500" />
                    <span className="text-sm text-gray-700">
                      Test recommendations and validation steps
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ReportModal;
