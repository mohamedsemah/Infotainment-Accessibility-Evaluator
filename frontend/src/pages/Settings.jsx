import React, { useState } from 'react';
import { 
  Save, 
  RefreshCw, 
  Palette, 
  Globe, 
  Bell,
  Shield,
  Database,
  ArrowLeft
} from 'lucide-react';
import useAppStore from '../store/useAppStore';

const SettingsPage = () => {
  const {
    theme,
    sidebarOpen,
    setTheme,
    setSidebarOpen,
    setCurrentPage,
    resetAll
  } = useAppStore();

  const [settings, setSettings] = useState({
    // Appearance
    theme: theme,
    sidebarOpen: sidebarOpen,
    
    // Analysis
    autoAnalyze: true,
    parallelAgents: true,
    maxConcurrentAgents: 3,
    
    // Notifications
    emailNotifications: false,
    desktopNotifications: true,
    progressUpdates: true,
    
    // LLM Integration
    llmProvider: 'none',
    llmApiKey: '',
    llmModel: 'gpt-4',
    
    // Advanced
    maxFileSize: 50,
    timeoutSeconds: 300,
    enableSandbox: true,
    autoApplyPatches: false
  });

  const [hasChanges, setHasChanges] = useState(false);

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
    setHasChanges(true);
  };

  const handleSave = () => {
    // Apply settings to store
    setTheme(settings.theme);
    setSidebarOpen(settings.sidebarOpen);
    
    // Save to localStorage
    localStorage.setItem('app-settings', JSON.stringify(settings));
    
    setHasChanges(false);
  };

  const handleReset = () => {
    const defaultSettings = {
      theme: 'light',
      sidebarOpen: true,
      autoAnalyze: true,
      parallelAgents: true,
      maxConcurrentAgents: 3,
      emailNotifications: false,
      desktopNotifications: true,
      progressUpdates: true,
      llmProvider: 'none',
      llmApiKey: '',
      llmModel: 'gpt-4',
      maxFileSize: 50,
      timeoutSeconds: 300,
      enableSandbox: true,
      autoApplyPatches: false
    };
    
    setSettings(defaultSettings);
    setHasChanges(true);
  };

  const handleBack = () => {
    setCurrentPage('results');
  };

  const llmProviders = [
    { id: 'none', name: 'Disabled', description: 'No LLM integration' },
    { id: 'openai', name: 'OpenAI', description: 'GPT-4, GPT-3.5-turbo' },
    { id: 'anthropic', name: 'Anthropic', description: 'Claude 3, Claude 2' },
    { id: 'deepseek', name: 'DeepSeek', description: 'DeepSeek Coder' }
  ];

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
                  Settings
                </h1>
                <p className="text-sm text-gray-600">
                  Configure your accessibility analysis preferences
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={handleReset}
                className="btn btn-outline"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Reset
              </button>
              <button
                onClick={handleSave}
                disabled={!hasChanges}
                className="btn btn-primary"
              >
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="space-y-6">
          {/* Appearance Settings */}
          <div className="card">
            <div className="card-header">
              <div className="flex items-center space-x-3">
                <Palette className="w-5 h-5 text-primary-600" />
                <h3 className="card-title text-lg">Appearance</h3>
              </div>
            </div>
            <div className="card-content space-y-4">
              <div>
                <label className="label">Theme</label>
                <select
                  value={settings.theme}
                  onChange={(e) => handleSettingChange('theme', e.target.value)}
                  className="input mt-1"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System</option>
                </select>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <label className="label">Sidebar</label>
                  <p className="text-sm text-gray-600">Show sidebar by default</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.sidebarOpen}
                    onChange={(e) => handleSettingChange('sidebarOpen', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
            </div>
          </div>

          {/* Analysis Settings */}
          <div className="card">
            <div className="card-header">
              <div className="flex items-center space-x-3">
                <Database className="w-5 h-5 text-primary-600" />
                <h3 className="card-title text-lg">Analysis</h3>
              </div>
            </div>
            <div className="card-content space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="label">Auto-analyze</label>
                  <p className="text-sm text-gray-600">Automatically start analysis after upload</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.autoAnalyze}
                    onChange={(e) => handleSettingChange('autoAnalyze', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <label className="label">Parallel Agents</label>
                  <p className="text-sm text-gray-600">Run multiple agents simultaneously</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.parallelAgents}
                    onChange={(e) => handleSettingChange('parallelAgents', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
              
              {settings.parallelAgents && (
                <div>
                  <label className="label">Max Concurrent Agents</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={settings.maxConcurrentAgents}
                    onChange={(e) => handleSettingChange('maxConcurrentAgents', parseInt(e.target.value))}
                    className="input mt-1 w-20"
                  />
                </div>
              )}
              
              <div>
                <label className="label">Max File Size (MB)</label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={settings.maxFileSize}
                  onChange={(e) => handleSettingChange('maxFileSize', parseInt(e.target.value))}
                  className="input mt-1 w-20"
                />
              </div>
              
              <div>
                <label className="label">Timeout (seconds)</label>
                <input
                  type="number"
                  min="60"
                  max="1800"
                  value={settings.timeoutSeconds}
                  onChange={(e) => handleSettingChange('timeoutSeconds', parseInt(e.target.value))}
                  className="input mt-1 w-20"
                />
              </div>
            </div>
          </div>

          {/* LLM Integration */}
          <div className="card">
            <div className="card-header">
              <div className="flex items-center space-x-3">
                <Globe className="w-5 h-5 text-primary-600" />
                <h3 className="card-title text-lg">LLM Integration</h3>
              </div>
            </div>
            <div className="card-content space-y-4">
              <div>
                <label className="label">Provider</label>
                <select
                  value={settings.llmProvider}
                  onChange={(e) => handleSettingChange('llmProvider', e.target.value)}
                  className="input mt-1"
                >
                  {llmProviders.map(provider => (
                    <option key={provider.id} value={provider.id}>
                      {provider.name} - {provider.description}
                    </option>
                  ))}
                </select>
              </div>
              
              {settings.llmProvider !== 'none' && (
                <>
                  <div>
                    <label className="label">API Key</label>
                    <input
                      type="password"
                      value={settings.llmApiKey}
                      onChange={(e) => handleSettingChange('llmApiKey', e.target.value)}
                      placeholder="Enter your API key"
                      className="input mt-1"
                    />
                    <p className="text-sm text-gray-600 mt-1">
                      Your API key is stored locally and never shared
                    </p>
                  </div>
                  
                  <div>
                    <label className="label">Model</label>
                    <select
                      value={settings.llmModel}
                      onChange={(e) => handleSettingChange('llmModel', e.target.value)}
                      className="input mt-1"
                    >
                      <option value="gpt-4">GPT-4</option>
                      <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                      <option value="claude-3-opus">Claude 3 Opus</option>
                      <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                      <option value="deepseek-coder">DeepSeek Coder</option>
                    </select>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Notifications */}
          <div className="card">
            <div className="card-header">
              <div className="flex items-center space-x-3">
                <Bell className="w-5 h-5 text-primary-600" />
                <h3 className="card-title text-lg">Notifications</h3>
              </div>
            </div>
            <div className="card-content space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="label">Desktop Notifications</label>
                  <p className="text-sm text-gray-600">Show browser notifications for progress updates</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.desktopNotifications}
                    onChange={(e) => handleSettingChange('desktopNotifications', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <label className="label">Progress Updates</label>
                  <p className="text-sm text-gray-600">Show real-time progress during analysis</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.progressUpdates}
                    onChange={(e) => handleSettingChange('progressUpdates', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
            </div>
          </div>

          {/* Advanced Settings */}
          <div className="card">
            <div className="card-header">
              <div className="flex items-center space-x-3">
                <Shield className="w-5 h-5 text-primary-600" />
                <h3 className="card-title text-lg">Advanced</h3>
              </div>
            </div>
            <div className="card-content space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="label">Enable Sandbox</label>
                  <p className="text-sm text-gray-600">Allow testing patches in isolated environment</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.enableSandbox}
                    onChange={(e) => handleSettingChange('enableSandbox', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <label className="label">Auto-apply Patches</label>
                  <p className="text-sm text-gray-600">Automatically apply high-confidence patches</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.autoApplyPatches}
                    onChange={(e) => handleSettingChange('autoApplyPatches', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
