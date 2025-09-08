import React, { useState, useEffect } from 'react';
import { Save, RotateCcw, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import useAppStore from '../store/useAppStore';

const Settings = () => {
  const { theme, setTheme, resetAll } = useAppStore();
  
  const [settings, setSettings] = useState({
    // LLM Settings
    llmProvider: 'none',
    openaiApiKey: '',
    anthropicApiKey: '',
    deepseekApiKey: '',
    openaiModel: 'gpt-4',
    anthropicModel: 'claude-3-sonnet-20240229',
    deepseekModel: 'deepseek-coder',
    
    // Analysis Settings
    clusteringMethod: 'semantic',
    similarityThreshold: 0.7,
    maxConcurrentAgents: 10,
    analysisTimeout: 1800,
    
    // UI Settings
    complianceLevel: 'AA',
    showAdvancedOptions: false,
    autoApplyPatches: false,
    enableSandbox: true,
    
    // Display Settings
    itemsPerPage: 20,
    showLineNumbers: true,
    showCodeSnippets: true,
    showMetrics: true
  });

  const [isSaving, setIsSaving] = useState(false);
  const [showApiKeys, setShowApiKeys] = useState({
    openai: false,
    anthropic: false,
    deepseek: false
  });
  const [saveStatus, setSaveStatus] = useState(null);

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('infotainment-a11y-settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(prev => ({ ...prev, ...parsed }));
      } catch (error) {
        console.error('Error loading settings:', error);
      }
    }
  }, []);

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleApiKeyToggle = (provider) => {
    setShowApiKeys(prev => ({ ...prev, [provider]: !prev[provider] }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveStatus(null);

    try {
      // Save to localStorage
      localStorage.setItem('infotainment-a11y-settings', JSON.stringify(settings));
      
      // In a real app, you'd also save to the backend
      // await apiClient.updateSettings(settings);
      
      setSaveStatus('success');
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset all settings to default values?')) {
      setSettings({
        llmProvider: 'none',
        openaiApiKey: '',
        anthropicApiKey: '',
        deepseekApiKey: '',
        openaiModel: 'gpt-4',
        anthropicModel: 'claude-3-sonnet-20240229',
        deepseekModel: 'deepseek-coder',
        clusteringMethod: 'semantic',
        similarityThreshold: 0.7,
        maxConcurrentAgents: 10,
        analysisTimeout: 1800,
        complianceLevel: 'AA',
        showAdvancedOptions: false,
        autoApplyPatches: false,
        enableSandbox: true,
        itemsPerPage: 20,
        showLineNumbers: true,
        showCodeSnippets: true,
        showMetrics: true
      });
      setSaveStatus('reset');
      setTimeout(() => setSaveStatus(null), 3000);
    }
  };

  const renderApiKeyField = (provider, key, label) => (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label} API Key
      </label>
      <div className="relative">
        <input
          type={showApiKeys[provider] ? 'text' : 'password'}
          value={settings[key]}
          onChange={(e) => handleSettingChange(key, e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          placeholder={`Enter your ${label} API key`}
        />
        <button
          type="button"
          onClick={() => handleApiKeyToggle(provider)}
          className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
        >
          {showApiKeys[provider] ? (
            <EyeOff className="w-4 h-4" />
          ) : (
            <Eye className="w-4 h-4" />
          )}
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
          <p className="text-gray-600">
            Configure your accessibility evaluation preferences and API keys.
          </p>
        </div>

        {/* Save Status */}
        {saveStatus && (
          <div className={`mb-6 p-4 rounded-lg flex items-center ${
            saveStatus === 'success' ? 'bg-green-50 text-green-800' :
            saveStatus === 'error' ? 'bg-red-50 text-red-800' :
            'bg-blue-50 text-blue-800'
          }`}>
            {saveStatus === 'success' && <CheckCircle className="w-5 h-5 mr-2" />}
            {saveStatus === 'error' && <AlertCircle className="w-5 h-5 mr-2" />}
            {saveStatus === 'reset' && <RotateCcw className="w-5 h-5 mr-2" />}
            {saveStatus === 'success' && 'Settings saved successfully!'}
            {saveStatus === 'error' && 'Error saving settings. Please try again.'}
            {saveStatus === 'reset' && 'Settings reset to default values.'}
          </div>
        )}

        <div className="space-y-8">
          {/* LLM Settings */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">LLM Provider Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  LLM Provider
                </label>
                <select
                  value={settings.llmProvider}
                  onChange={(e) => handleSettingChange('llmProvider', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="none">None (Heuristic Only)</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="deepseek">DeepSeek</option>
                </select>
              </div>

              {settings.llmProvider === 'openai' && (
                <div className="space-y-4">
                  {renderApiKeyField('openai', 'openaiApiKey', 'OpenAI')}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Model
                    </label>
                    <select
                      value={settings.openaiModel}
                      onChange={(e) => handleSettingChange('openaiModel', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="gpt-4">GPT-4</option>
                      <option value="gpt-4-turbo">GPT-4 Turbo</option>
                      <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    </select>
                  </div>
                </div>
              )}

              {settings.llmProvider === 'anthropic' && (
                <div className="space-y-4">
                  {renderApiKeyField('anthropic', 'anthropicApiKey', 'Anthropic')}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Model
                    </label>
                    <select
                      value={settings.anthropicModel}
                      onChange={(e) => handleSettingChange('anthropicModel', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                      <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                      <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                    </select>
                  </div>
                </div>
              )}

              {settings.llmProvider === 'deepseek' && (
                <div className="space-y-4">
                  {renderApiKeyField('deepseek', 'deepseekApiKey', 'DeepSeek')}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Model
                    </label>
                    <select
                      value={settings.deepseekModel}
                      onChange={(e) => handleSettingChange('deepseekModel', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="deepseek-coder">DeepSeek Coder</option>
                      <option value="deepseek-chat">DeepSeek Chat</option>
                    </select>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Analysis Settings */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Analysis Settings</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Clustering Method
                </label>
                <select
                  value={settings.clusteringMethod}
                  onChange={(e) => handleSettingChange('clusteringMethod', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="semantic">Semantic</option>
                  <option value="rule_based">Rule-based</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Similarity Threshold: {settings.similarityThreshold}
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  value={settings.similarityThreshold}
                  onChange={(e) => handleSettingChange('similarityThreshold', parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Concurrent Agents
                </label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={settings.maxConcurrentAgents}
                  onChange={(e) => handleSettingChange('maxConcurrentAgents', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Analysis Timeout (seconds)
                </label>
                <input
                  type="number"
                  min="300"
                  max="3600"
                  value={settings.analysisTimeout}
                  onChange={(e) => handleSettingChange('analysisTimeout', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
          </div>

          {/* UI Settings */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">UI Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  WCAG Compliance Level
                </label>
                <select
                  value={settings.complianceLevel}
                  onChange={(e) => handleSettingChange('complianceLevel', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="A">Level A</option>
                  <option value="AA">Level AA</option>
                  <option value="AAA">Level AAA</option>
                </select>
              </div>

              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.autoApplyPatches}
                    onChange={(e) => handleSettingChange('autoApplyPatches', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Auto-apply patches</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.enableSandbox}
                    onChange={(e) => handleSettingChange('enableSandbox', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enable sandbox testing</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.showLineNumbers}
                    onChange={(e) => handleSettingChange('showLineNumbers', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Show line numbers</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.showCodeSnippets}
                    onChange={(e) => handleSettingChange('showCodeSnippets', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Show code snippets</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.showMetrics}
                    onChange={(e) => handleSettingChange('showMetrics', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Show metrics</span>
                </label>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between">
            <button
              onClick={handleReset}
              className="btn btn-outline"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Reset to Defaults
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="btn btn-primary"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Save Settings
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;