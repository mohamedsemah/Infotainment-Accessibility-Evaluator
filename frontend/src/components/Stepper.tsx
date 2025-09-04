import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StepperProps {
  stages: Array<{
    name: string;
    status: 'completed' | 'in-progress' | 'failed' | 'pending';
    duration?: number;
  }>;
}

const Stepper: React.FC<StepperProps> = ({ stages }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'in-progress':
        return <Clock className="h-5 w-5 text-blue-600 animate-spin" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return <div className="h-5 w-5 rounded-full border-2 border-gray-300" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'in-progress':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'failed':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-600';
    }
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return '';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {stages.map((stage, index) => (
          <React.Fragment key={index}>
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="flex flex-col items-center"
            >
              <div className={cn(
                "flex items-center justify-center w-12 h-12 rounded-full border-2 transition-colors",
                getStatusColor(stage.status)
              )}>
                {getStatusIcon(stage.status)}
              </div>
              <div className="mt-2 text-center">
                <p className="text-sm font-medium">{stage.name}</p>
                {stage.duration && (
                  <p className="text-xs text-gray-500 mt-1">
                    {formatDuration(stage.duration)}
                  </p>
                )}
              </div>
            </motion.div>
            
            {index < stages.length - 1 && (
              <motion.div
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ delay: index * 0.1 + 0.2, duration: 0.3 }}
                className="flex-1 h-0.5 bg-gray-200 mx-4"
              >
                <motion.div
                  initial={{ scaleX: 0 }}
                  animate={{ 
                    scaleX: stages[index].status === 'completed' ? 1 : 0 
                  }}
                  transition={{ delay: index * 0.1 + 0.4, duration: 0.3 }}
                  className="h-full bg-green-500 origin-left"
                />
              </motion.div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

export default Stepper;
