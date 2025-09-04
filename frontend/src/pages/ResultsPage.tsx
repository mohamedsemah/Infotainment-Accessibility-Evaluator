import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Download, FileText, Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import Stepper from '@/components/Stepper';
import CandidateTable from '@/components/CandidateTable';
import MetricTable from '@/components/MetricTable';
import DecisionTable from '@/components/DecisionTable';
import FixCard from '@/components/FixCard';
import ReportModal from '@/components/ReportModal';
import { api } from '@/api/client';
import { useToast } from '@/hooks/use-toast';

interface PipelineResponse {
  session_id: string;
  candidates: any[];
  metrics: any[];
  decisions: any[];
  fixes: any[];
  timings: {
    llm1_discovery_ms: number;
    llm2_metrics_ms: number;
    llm3_validation_ms: number;
    llm4_fixes_ms: number;
    total_ms: number;
  };
  cost_estimate: any;
  model_map_used: any;
}

const ResultsPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [pipelineData, setPipelineData] = useState<PipelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showReportModal, setShowReportModal] = useState(false);

  useEffect(() => {
    if (sessionId) {
      loadPipelineResults();
    }
  }, [sessionId]);

  const loadPipelineResults = async () => {
    try {
      setLoading(true);
      // In a real implementation, you would fetch the results from the backend
      // For now, we'll simulate the data structure
      const mockData: PipelineResponse = {
        session_id: sessionId!,
        candidates: [
          {
            id: "1",
            rule_id: "1.1.1",
            title: "Missing alt text",
            description: "Image element lacks alt attribute",
            evidence: [{
              file_path: "index.html",
              start_line: 10,
              end_line: 10,
              code_snippet: '<img src="car.png">'
            }],
            tags: ["images", "alt-text"],
            llm_model: "claude-opus-4-1-20250805",
            confidence: "high"
          },
          {
            id: "2",
            rule_id: "1.4.3",
            title: "Insufficient contrast",
            description: "Text and background colors have insufficient contrast ratio",
            evidence: [{
              file_path: "styles.css",
              start_line: 5,
              end_line: 8,
              code_snippet: '.info { color: #777; background: #808080; }'
            }],
            tags: ["contrast", "colors"],
            llm_model: "claude-opus-4-1-20250805",
            confidence: "medium"
          }
        ],
        metrics: [
          {
            name: "contrast_ratio",
            scope_id: "styles.css:.info",
            value: 2.5,
            unit: "ratio",
            computed_from: [],
            notes: "Below WCAG AA threshold of 4.5",
            llm_model: "deepseek-chat"
          }
        ],
        decisions: [
          {
            candidate_id: "1",
            rule_id: "1.1.1",
            passed: false,
            severity: "serious",
            reasoning: "Image lacks alt attribute, violating WCAG 1.1.1",
            metrics_used: {},
            llm_model: "grok-4"
          },
          {
            candidate_id: "2",
            rule_id: "1.4.3",
            passed: false,
            severity: "moderate",
            reasoning: "Contrast ratio 2.5 is below threshold 4.5",
            metrics_used: { contrast_ratio: 2.5 },
            llm_model: "grok-4"
          }
        ],
        fixes: [
          {
            candidate_id: "1",
            rule_id: "1.1.1",
            patch_unified_diff: "--- a/index.html\n+++ b/index.html\n@@ -1,1 +1,1 @@\n-<img src=\"car.png\">\n+<img src=\"car.png\" alt=\"Car dashboard icon\">",
            summary: "Add descriptive alt text to image",
            side_effects: ["May affect SEO"],
            test_suggestions: ["Test with screen reader", "Verify alt text is descriptive"],
            llm_model: "gpt-5"
          }
        ],
        timings: {
          llm1_discovery_ms: 1200,
          llm2_metrics_ms: 800,
          llm3_validation_ms: 600,
          llm4_fixes_ms: 1000,
          total_ms: 3600
        },
        cost_estimate: {
          total_estimated_cost_usd: 0.05
        },
        model_map_used: {
          llm1: "claude-opus-4-1-20250805",
          llm2: "deepseek-chat",
          llm3: "grok-4",
          llm4: "gpt-5"
        }
      };
      
      setPipelineData(mockData);
    } catch (error: any) {
      setError(error.message);
      toast({
        title: "Failed to load results",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getSeverityStats = () => {
    if (!pipelineData) return { total: 0, passed: 0, failed: 0, bySeverity: {} };
    
    const decisions = pipelineData.decisions;
    const passed = decisions.filter(d => d.passed).length;
    const failed = decisions.filter(d => !d.passed).length;
    
    const bySeverity = failed > 0 ? decisions
      .filter(d => !d.passed)
      .reduce((acc, d) => {
        acc[d.severity] = (acc[d.severity] || 0) + 1;
        return acc;
      }, {} as Record<string, number>) : {};
    
    return {
      total: decisions.length,
      passed,
      failed,
      bySeverity
    };
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading pipeline results...</p>
        </div>
      </div>
    );
  }

  if (error || !pipelineData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-red-600">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              {error || "Failed to load pipeline results"}
            </p>
            <Button onClick={() => navigate('/')} variant="outline">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Upload
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const stats = getSeverityStats();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <Button
              onClick={() => navigate('/')}
              variant="outline"
              className="mb-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Upload
            </Button>
            
            <Button
              onClick={() => setShowReportModal(true)}
              className="mb-4"
            >
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Accessibility Analysis Results
          </h1>
          <p className="text-gray-600">
            Session: {pipelineData.session_id} • Completed in {formatDuration(pipelineData.timings.total_ms)}
          </p>
        </motion.div>

        {/* Pipeline Progress */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <Stepper
            stages={[
              { name: "Discovery", status: "completed", duration: pipelineData.timings.llm1_discovery_ms },
              { name: "Metrics", status: "completed", duration: pipelineData.timings.llm2_metrics_ms },
              { name: "Validation", status: "completed", duration: pipelineData.timings.llm3_validation_ms },
              { name: "Fixes", status: "completed", duration: pipelineData.timings.llm4_fixes_ms }
            ]}
          />
        </motion.div>

        {/* Summary Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
        >
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FileText className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
                  <p className="text-sm text-gray-600">Total Issues</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-600">{stats.passed}</p>
                  <p className="text-sm text-gray-600">Passed</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-red-100 rounded-lg">
                  <XCircle className="h-5 w-5 text-red-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-red-600">{stats.failed}</p>
                  <p className="text-sm text-gray-600">Failed</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <Clock className="h-5 w-5 text-orange-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{formatDuration(pipelineData.timings.total_ms)}</p>
                  <p className="text-sm text-gray-600">Total Time</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Results Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Tabs defaultValue="discovery" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="discovery">
                Discovery ({pipelineData.candidates.length})
              </TabsTrigger>
              <TabsTrigger value="metrics">
                Metrics ({pipelineData.metrics.length})
              </TabsTrigger>
              <TabsTrigger value="validation">
                Validation ({pipelineData.decisions.length})
              </TabsTrigger>
              <TabsTrigger value="fixes">
                Fixes ({pipelineData.fixes.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="discovery" className="mt-6">
              <CandidateTable candidates={pipelineData.candidates} />
            </TabsContent>

            <TabsContent value="metrics" className="mt-6">
              <MetricTable metrics={pipelineData.metrics} />
            </TabsContent>

            <TabsContent value="validation" className="mt-6">
              <DecisionTable decisions={pipelineData.decisions} />
            </TabsContent>

            <TabsContent value="fixes" className="mt-6">
              <div className="space-y-4">
                {pipelineData.fixes.map((fix, index) => (
                  <FixCard key={index} fix={fix} />
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </motion.div>

        {/* Report Modal */}
        {showReportModal && (
          <ReportModal
            pipelineData={pipelineData}
            onClose={() => setShowReportModal(false)}
          />
        )}
      </div>
    </div>
  );
};

export default ResultsPage;
