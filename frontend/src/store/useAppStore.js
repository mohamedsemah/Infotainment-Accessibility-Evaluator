import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const useAppStore = create(
  devtools(
    persist(
      (set, get) => ({
        // UI State
        sidebarOpen: true,
        theme: 'light',
        currentPage: 'upload',
        
        // Upload State
        uploadId: null,
        uploadProgress: 0,
        uploadStatus: 'idle', // 'idle', 'uploading', 'success', 'error'
        uploadError: null,
        
        // Analysis State
        analysisStatus: 'idle', // 'idle', 'analyzing', 'success', 'error'
        analysisError: null,
        preScanResults: null,
        
        // Planning State
        planStatus: 'idle', // 'idle', 'planning', 'success', 'error'
        planError: null,
        executionPlan: null,
        
        // Agent Execution State
        agentStatus: 'idle', // 'idle', 'running', 'success', 'error'
        agentError: null,
        runningAgents: [],
        completedAgents: [],
        agentProgress: {},
        
        // Findings State
        rawFindings: [],
        clusters: [],
        selectedCluster: null,
        selectedFinding: null,
        
        // Filtering State
        filters: {
          severity: 'all', // 'all', 'critical', 'high', 'medium', 'low'
          confidence: 'all', // 'all', 'high', 'medium', 'low'
          agent: 'all', // 'all', 'contrast', 'seizure', 'language', 'aria', 'state', 'triage', 'token'
          status: 'all', // 'all', 'open', 'fixed', 'ignored'
          search: ''
        },
        
        // Patching State
        patches: [],
        patchStatus: 'idle', // 'idle', 'generating', 'success', 'error'
        patchError: null,
        appliedPatches: [],
        
        // Sandbox State
        sandboxStatus: 'idle', // 'idle', 'applying', 'rechecking', 'success', 'error'
        sandboxError: null,
        sandboxResults: null,
        
        // Report State
        reportStatus: 'idle', // 'idle', 'generating', 'success', 'error'
        reportError: null,
        reportData: null,
        
        // Progress State
        overallProgress: 0,
        currentStep: '',
        isProcessing: false,
        
        // Actions
        setSidebarOpen: (open) => set({ sidebarOpen: open }),
        setTheme: (theme) => set({ theme }),
        setCurrentPage: (page) => set({ currentPage: page }),
        
        // Upload Actions
        setUploadId: (uploadId) => set({ uploadId }),
        setUploadProgress: (progress) => set({ uploadProgress: progress }),
        setUploadStatus: (status) => set({ uploadStatus: status }),
        setUploadError: (error) => set({ uploadError: error }),
        resetUpload: () => set({
          uploadId: null,
          uploadProgress: 0,
          uploadStatus: 'idle',
          uploadError: null
        }),
        
        // Analysis Actions
        setAnalysisStatus: (status) => set({ analysisStatus: status }),
        setAnalysisError: (error) => set({ analysisError: error }),
        setPreScanResults: (results) => set({ preScanResults: results }),
        resetAnalysis: () => set({
          analysisStatus: 'idle',
          analysisError: null,
          preScanResults: null
        }),
        
        // Planning Actions
        setPlanStatus: (status) => set({ planStatus: status }),
        setPlanError: (error) => set({ planError: error }),
        setExecutionPlan: (plan) => set({ executionPlan: plan }),
        resetPlan: () => set({
          planStatus: 'idle',
          planError: null,
          executionPlan: null
        }),
        
        // Agent Actions
        setAgentStatus: (status) => set({ agentStatus: status }),
        setAgentError: (error) => set({ agentError: error }),
        setRunningAgents: (agents) => set({ runningAgents: agents }),
        setCompletedAgents: (agents) => set({ completedAgents: agents }),
        setAgentProgress: (agentId, progress) => set((state) => ({
          agentProgress: { ...state.agentProgress, [agentId]: progress }
        })),
        resetAgents: () => set({
          agentStatus: 'idle',
          agentError: null,
          runningAgents: [],
          completedAgents: [],
          agentProgress: {}
        }),
        
        // Findings Actions
        setRawFindings: (findings) => set({ rawFindings: findings }),
        setClusters: (clusters) => set({ clusters }),
        setSelectedCluster: (cluster) => set({ selectedCluster: cluster }),
        setSelectedFinding: (finding) => set({ selectedFinding: finding }),
        resetFindings: () => set({
          rawFindings: [],
          clusters: [],
          selectedCluster: null,
          selectedFinding: null
        }),
        
        // Filter Actions
        setFilters: (filters) => set({ filters: { ...get().filters, ...filters } }),
        resetFilters: () => set({
          filters: {
            severity: 'all',
            confidence: 'all',
            agent: 'all',
            status: 'all',
            search: ''
          }
        }),
        
        // Patch Actions
        setPatches: (patches) => set({ patches }),
        setPatchStatus: (status) => set({ patchStatus: status }),
        setPatchError: (error) => set({ patchError: error }),
        setAppliedPatches: (patches) => set({ appliedPatches: patches }),
        resetPatches: () => set({
          patches: [],
          patchStatus: 'idle',
          patchError: null,
          appliedPatches: []
        }),
        
        // Sandbox Actions
        setSandboxStatus: (status) => set({ sandboxStatus: status }),
        setSandboxError: (error) => set({ sandboxError: error }),
        setSandboxResults: (results) => set({ sandboxResults: results }),
        resetSandbox: () => set({
          sandboxStatus: 'idle',
          sandboxError: null,
          sandboxResults: null
        }),
        
        // Report Actions
        setReportStatus: (status) => set({ reportStatus: status }),
        setReportError: (error) => set({ reportError: error }),
        setReportData: (data) => set({ reportData: data }),
        resetReport: () => set({
          reportStatus: 'idle',
          reportError: null,
          reportData: null
        }),
        
        // Progress Actions
        setOverallProgress: (progress) => set({ overallProgress: progress }),
        setCurrentStep: (step) => set({ currentStep: step }),
        setIsProcessing: (processing) => set({ isProcessing: processing }),
        
        // Reset All
        resetAll: () => set({
          sidebarOpen: true,
          theme: 'light',
          currentPage: 'upload',
          uploadId: null,
          uploadProgress: 0,
          uploadStatus: 'idle',
          uploadError: null,
          analysisStatus: 'idle',
          analysisError: null,
          preScanResults: null,
          planStatus: 'idle',
          planError: null,
          executionPlan: null,
          agentStatus: 'idle',
          agentError: null,
          runningAgents: [],
          completedAgents: [],
          agentProgress: {},
          rawFindings: [],
          clusters: [],
          selectedCluster: null,
          selectedFinding: null,
          filters: {
            severity: 'all',
            confidence: 'all',
            agent: 'all',
            status: 'all',
            search: ''
          },
          patches: [],
          patchStatus: 'idle',
          patchError: null,
          appliedPatches: [],
          sandboxStatus: 'idle',
          sandboxError: null,
          sandboxResults: null,
          reportStatus: 'idle',
          reportError: null,
          reportData: null,
          overallProgress: 0,
          currentStep: '',
          isProcessing: false
        })
      }),
      {
        name: 'infotainment-a11y-store',
        partialize: (state) => ({
          theme: state.theme,
          sidebarOpen: state.sidebarOpen,
          filters: state.filters
        })
      }
    ),
    {
      name: 'infotainment-a11y-store'
    }
  )
);

export default useAppStore;
