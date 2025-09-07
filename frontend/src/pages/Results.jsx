import React, { useEffect, useState } from 'react';
import { 
  Filter, 
  Search, 
  Download, 
  RefreshCw, 
  Eye, 
  EyeOff,
  AlertTriangle,
  CheckCircle,
  Info,
  X
} from 'lucide-react';
import useAppStore from '../store/useAppStore';
import ClusterCard from '../components/ClusterCard';
import Filters from '../components/Filters';
import ProgressToast from '../components/ProgressToast';
import apiClient from '../api/client';

const ResultsPage = () => {
  const {
    uploadId,
    clusters,
    rawFindings,
    filters,
    selectedCluster,
    selectedFinding,
    isProcessing,
    currentStep,
    overallProgress,
    setClusters,
    setRawFindings,
    setSelectedCluster,
    setSelectedFinding,
    setFilters,
    setCurrentPage,
    setError
  } = useAppStore();

  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState(filters.search);

  // Load data on component mount
  useEffect(() => {
    if (uploadId && clusters.length === 0) {
      loadResults();
    }
  }, [uploadId]);

  const loadResults = async () => {
    try {
      console.log('Loading results for upload:', uploadId);
      
      // Step 1: Run pre-scan analysis
      const analysisResult = await apiClient.analyzeUpload(uploadId);
      console.log('Analysis result:', analysisResult);
      
      // Step 2: Create agent plan
      const plan = await apiClient.createPlan(uploadId, analysisResult);
      console.log('Agent plan:', plan);
      
      // Step 3: Execute agents
      const agentResults = await apiClient.runAgents(uploadId);
      console.log('Agent results:', agentResults);
      
      // Step 4: Cluster findings
      const findings = agentResults.all_findings || [];
      console.log('Findings to cluster:', findings);
      console.log('Findings count:', findings.length);
      
      const clusters = await apiClient.clusterFindings(findings, uploadId);
      console.log('Clustered findings:', clusters);
      
      // Update store with results
      setClusters(clusters.clusters || []);
      setRawFindings(agentResults.all_findings || []);
      
    } catch (error) {
      console.error('Failed to load results:', error);
      setError('Failed to load analysis results');
    }
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    setFilters({ search: query });
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleClusterSelect = (cluster) => {
    setSelectedCluster(cluster);
  };

  const handleFindingSelect = (finding) => {
    setSelectedFinding(finding);
  };

  const handleGenerateReport = async () => {
    try {
      console.log('Generating report for upload:', uploadId);
      await apiClient.downloadReport(uploadId, 'html');
      console.log('Report generated successfully');
    } catch (error) {
      console.error('Failed to generate report:', error);
      setError(`Failed to generate report: ${error.message}`);
    }
  };

  const handleRecheck = async () => {
    try {
      // Trigger recheck in sandbox
      console.log('Rechecking in sandbox...');
    } catch (error) {
      console.error('Failed to recheck:', error);
    }
  };

  const filteredClusters = clusters.filter(cluster => {
    // Apply search filter
    if (filters.search && !cluster.title.toLowerCase().includes(filters.search.toLowerCase())) {
      return false;
    }

    // Apply severity filter
    if (filters.severity !== 'all' && cluster.severity !== filters.severity) {
      return false;
    }

    // Apply confidence filter
    if (filters.confidence !== 'all' && cluster.confidence !== filters.confidence) {
      return false;
    }

    // Apply agent filter
    if (filters.agent !== 'all' && cluster.agent !== filters.agent) {
      return false;
    }

    return true;
  });

  const getSeverityCounts = () => {
    const counts = { critical: 0, high: 0, medium: 0, low: 0 };
    clusters.forEach(cluster => {
      counts[cluster.severity] = (counts[cluster.severity] || 0) + cluster.occurrences.length;
    });
    return counts;
  };

  const severityCounts = getSeverityCounts();
  const totalFindings = Object.values(severityCounts).reduce((sum, count) => sum + count, 0);

  if (!uploadId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-warning-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Analysis Found</h2>
          <p className="text-gray-600 mb-6">Please upload your code first to see results.</p>
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
              <h1 className="text-xl font-semibold text-gray-900">
                Accessibility Analysis Results
              </h1>
              {totalFindings > 0 && (
                <span className="badge badge-error">
                  {totalFindings} issues found
                </span>
              )}
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`btn btn-outline ${showFilters ? 'bg-gray-100' : ''}`}
              >
                <Filter className="w-4 h-4 mr-2" />
                Filters
                {Object.values(filters).some(f => f !== 'all' && f !== '') && (
                  <span className="ml-2 w-2 h-2 bg-primary-500 rounded-full" />
                )}
              </button>
              
              <button
                onClick={handleRecheck}
                className="btn btn-outline"
                disabled={isProcessing}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isProcessing ? 'animate-spin' : ''}`} />
                Recheck
              </button>
              
              <button
                onClick={handleGenerateReport}
                className="btn btn-primary"
              >
                <Download className="w-4 h-4 mr-2" />
                Export Report
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Toast */}
      {isProcessing && (
        <ProgressToast
          progress={overallProgress}
          step={currentStep}
        />
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Main Content */}
          <div className="flex-1">
            {/* Search and Stats */}
            <div className="mb-6">
              <div className="flex flex-col sm:flex-row gap-4 mb-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search findings..."
                    value={searchQuery}
                    onChange={(e) => handleSearch(e.target.value)}
                    className="input pl-10"
                  />
                </div>
              </div>

              {/* Severity Summary */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <div className="card-content p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Critical</p>
                        <p className="text-2xl font-bold text-error-600">{severityCounts.critical}</p>
                      </div>
                      <AlertTriangle className="w-8 h-8 text-error-500" />
                    </div>
                  </div>
                </div>
                
                <div className="card">
                  <div className="card-content p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">High</p>
                        <p className="text-2xl font-bold text-warning-600">{severityCounts.high}</p>
                      </div>
                      <AlertTriangle className="w-8 h-8 text-warning-500" />
                    </div>
                  </div>
                </div>
                
                <div className="card">
                  <div className="card-content p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Medium</p>
                        <p className="text-2xl font-bold text-primary-600">{severityCounts.medium}</p>
                      </div>
                      <Info className="w-8 h-8 text-primary-500" />
                    </div>
                  </div>
                </div>
                
                <div className="card">
                  <div className="card-content p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Low</p>
                        <p className="text-2xl font-bold text-gray-600">{severityCounts.low}</p>
                      </div>
                      <Info className="w-8 h-8 text-gray-500" />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Clusters List */}
            <div className="space-y-4">
              {filteredClusters.length === 0 ? (
                <div className="card">
                  <div className="card-content p-12 text-center">
                    <CheckCircle className="w-16 h-16 text-success-500 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      No Issues Found
                    </h3>
                    <p className="text-gray-600">
                      Great! Your infotainment UI appears to be accessible.
                    </p>
                  </div>
                </div>
              ) : (
                filteredClusters.map((cluster) => (
                  <ClusterCard
                    key={cluster.id}
                    cluster={cluster}
                    isSelected={selectedCluster?.id === cluster.id}
                    onSelect={() => handleClusterSelect(cluster)}
                    onFindingSelect={handleFindingSelect}
                  />
                ))
              )}
            </div>
          </div>

          {/* Filters Sidebar */}
          {showFilters && (
            <div className="lg:w-80">
              <div className="card sticky top-6">
                <div className="card-header">
                  <div className="flex items-center justify-between">
                    <h3 className="card-title text-lg">Filters</h3>
                    <button
                      onClick={() => setShowFilters(false)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                </div>
                <div className="card-content">
                  <Filters
                    filters={filters}
                    onFilterChange={handleFilterChange}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
