import React, { useState, useEffect } from 'react';
import { 
  Download, 
  FileText, 
  FileSpreadsheet, 
  FileCode,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Info,
  ArrowLeft
} from 'lucide-react';
import useAppStore from '../store/useAppStore';
import apiClient from '../api/client';

const ReportPage = () => {
  const {
    uploadId,
    clusters,
    rawFindings,
    reportStatus,
    reportError,
    setCurrentPage,
    setReportStatus,
    setReportError
  } = useAppStore();

  const [selectedFormat, setSelectedFormat] = useState('html');
  const [isGenerating, setIsGenerating] = useState(false);

  const formats = [
    {
      id: 'html',
      name: 'HTML Report',
      description: 'Interactive web report with charts and detailed findings',
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      id: 'pdf',
      name: 'PDF Report',
      description: 'Print-ready PDF document for sharing and archiving',
      icon: FileText,
      color: 'text-red-600',
      bgColor: 'bg-red-50'
    },
    {
      id: 'csv',
      name: 'CSV Export',
      description: 'Spreadsheet format for data analysis and filtering',
      icon: FileSpreadsheet,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      id: 'json',
      name: 'JSON Export',
      description: 'Machine-readable format for integration and automation',
      icon: FileCode,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    }
  ];

  const handleGenerateReport = async () => {
    if (!uploadId) return;

    setIsGenerating(true);
    setReportStatus('generating');
    setReportError(null);

    try {
      await apiClient.downloadReport(uploadId, selectedFormat);
      setReportStatus('success');
    } catch (error) {
      setReportError(error.message);
      setReportStatus('error');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleBack = () => {
    setCurrentPage('results');
  };

  const getSeverityStats = () => {
    const stats = { critical: 0, high: 0, medium: 0, low: 0 };
    clusters.forEach(cluster => {
      stats[cluster.severity] = (stats[cluster.severity] || 0) + cluster.occurrences.length;
    });
    return stats;
  };

  const getAgentStats = () => {
    const stats = {};
    clusters.forEach(cluster => {
      stats[cluster.agent] = (stats[cluster.agent] || 0) + cluster.occurrences.length;
    });
    return stats;
  };

  const severityStats = getSeverityStats();
  const agentStats = getAgentStats();
  const totalFindings = Object.values(severityStats).reduce((sum, count) => sum + count, 0);

  if (!uploadId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-warning-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Analysis Found</h2>
          <p className="text-gray-600 mb-6">Please upload your code first to generate reports.</p>
          <button
            onClick={() => setCurrentPage('upload')}
            className="btn btn-primary"
          >
            Go to Upload
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleBack}
                className="text-gray-400 hover:text-gray-600"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Generate Report
                </h1>
                <p className="text-sm text-gray-600">
                  Export your accessibility analysis results
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Report Options */}
          <div className="lg:col-span-1">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title text-lg">Report Format</h3>
                <p className="card-description">
                  Choose the format that best suits your needs
                </p>
              </div>
              <div className="card-content space-y-3">
                {formats.map((format) => {
                  const Icon = format.icon;
                  return (
                    <div
                      key={format.id}
                      className={`p-4 rounded-lg border cursor-pointer transition-all ${
                        selectedFormat === format.id
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedFormat(format.id)}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`p-2 rounded-lg ${format.bgColor}`}>
                          <Icon className={`w-5 h-5 ${format.color}`} />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">
                            {format.name}
                          </h4>
                          <p className="text-sm text-gray-600 mt-1">
                            {format.description}
                          </p>
                        </div>
                        {selectedFormat === format.id && (
                          <CheckCircle className="w-5 h-5 text-primary-600" />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="card-footer">
                <button
                  onClick={handleGenerateReport}
                  disabled={isGenerating}
                  className="btn btn-primary w-full"
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4 mr-2" />
                      Generate Report
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Error Display */}
            {reportError && (
              <div className="mt-4 card border-error-200 bg-error-50">
                <div className="card-content p-4">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-error-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-error-900">Generation Failed</h4>
                      <p className="text-sm text-error-700 mt-1">{reportError}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Report Preview */}
          <div className="lg:col-span-2">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title text-lg">Report Preview</h3>
                <p className="card-description">
                  Summary of findings that will be included in your report
                </p>
              </div>
              <div className="card-content">
                {/* Summary Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-error-600">
                      {severityStats.critical}
                    </div>
                    <div className="text-sm text-gray-600">Critical</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-warning-600">
                      {severityStats.high}
                    </div>
                    <div className="text-sm text-gray-600">High</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary-600">
                      {severityStats.medium}
                    </div>
                    <div className="text-sm text-gray-600">Medium</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-600">
                      {severityStats.low}
                    </div>
                    <div className="text-sm text-gray-600">Low</div>
                  </div>
                </div>

                {/* Agent Breakdown */}
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Findings by Agent</h4>
                  <div className="space-y-2">
                    {Object.entries(agentStats).map(([agent, count]) => (
                      <div key={agent} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 capitalize">
                          {agent.replace('_', ' ')} Agent
                        </span>
                        <span className="text-sm font-medium text-gray-900">
                          {count} findings
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Clusters Summary */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Issue Clusters</h4>
                  <div className="space-y-2">
                    {clusters.slice(0, 5).map((cluster) => (
                      <div key={cluster.id} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 truncate">
                          {cluster.title}
                        </span>
                        <div className="flex items-center space-x-2">
                          <span className={`badge badge-sm ${
                            cluster.severity === 'critical' ? 'badge-error' :
                            cluster.severity === 'high' ? 'badge-warning' :
                            cluster.severity === 'medium' ? 'badge-primary' :
                            'badge-secondary'
                          }`}>
                            {cluster.severity}
                          </span>
                          <span className="text-sm text-gray-500">
                            {cluster.occurrences.length}
                          </span>
                        </div>
                      </div>
                    ))}
                    {clusters.length > 5 && (
                      <div className="text-sm text-gray-500 text-center pt-2">
                        ... and {clusters.length - 5} more clusters
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Report Features */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="card">
                <div className="card-content p-4">
                  <div className="flex items-start space-x-3">
                    <Info className="w-5 h-5 text-primary-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-gray-900">What's Included</h4>
                      <ul className="text-sm text-gray-600 mt-2 space-y-1">
                        <li>• Detailed findings with evidence</li>
                        <li>• WCAG 2.2 compliance status</li>
                        <li>• Automated fix suggestions</li>
                        <li>• Before/after code comparisons</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="card">
                <div className="card-content p-4">
                  <div className="flex items-start space-x-3">
                    <CheckCircle className="w-5 h-5 text-success-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-gray-900">Export Benefits</h4>
                      <ul className="text-sm text-gray-600 mt-2 space-y-1">
                        <li>• Share with stakeholders</li>
                        <li>• Track progress over time</li>
                        <li>• Integrate with CI/CD</li>
                        <li>• Archive for compliance</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportPage;
