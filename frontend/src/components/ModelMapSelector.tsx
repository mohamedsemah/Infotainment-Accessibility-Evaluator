import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Settings, Brain, Zap, Shield, Wrench } from 'lucide-react';

const ModelMapSelector: React.FC = () => {
  const modelMap = {
    llm1: "claude-opus-4-1-20250805",
    llm2: "deepseek-chat",
    llm3: "grok-4",
    llm4: "gpt-5"
  };

  const stageInfo = [
    {
      stage: 1,
      name: "Discovery",
      model: modelMap.llm1,
      description: "Find potential accessibility issues",
      icon: Brain,
      color: "blue"
    },
    {
      stage: 2,
      name: "Metrics",
      model: modelMap.llm2,
      description: "Compute WCAG measurements",
      icon: Zap,
      color: "green"
    },
    {
      stage: 3,
      name: "Validation",
      model: modelMap.llm3,
      description: "Make pass/fail decisions",
      icon: Shield,
      color: "orange"
    },
    {
      stage: 4,
      name: "Fixes",
      model: modelMap.llm4,
      description: "Generate patch suggestions",
      icon: Wrench,
      color: "purple"
    }
  ];

  const getColorClasses = (color: string) => {
    const colors = {
      blue: "bg-blue-50 border-blue-200 text-blue-800",
      green: "bg-green-50 border-green-200 text-green-800",
      orange: "bg-orange-50 border-orange-200 text-orange-800",
      purple: "bg-purple-50 border-purple-200 text-purple-800"
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Settings className="h-4 w-4" />
        <span className="font-medium">Premium Model Configuration</span>
        <Badge variant="secondary" className="ml-auto">Read Only</Badge>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {stageInfo.map((stage) => {
          const Icon = stage.icon;
          return (
            <div
              key={stage.stage}
              className={`p-3 rounded-lg border ${getColorClasses(stage.color)}`}
            >
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center text-xs font-bold">
                    {stage.stage}
                  </div>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm">{stage.name}</div>
                  <div className="text-xs opacity-75 truncate">{stage.description}</div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-mono">{stage.model}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <div className="text-xs text-gray-600">
          <p className="font-medium mb-1">Configuration Notes:</p>
          <ul className="space-y-1 text-xs">
            <li>• Claude Opus 4.1 for comprehensive issue discovery</li>
            <li>• DeepSeek V3 for fast metric computation</li>
            <li>• Grok-4 for reliable validation decisions</li>
            <li>• GPT-5 for high-quality fix generation</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ModelMapSelector;
