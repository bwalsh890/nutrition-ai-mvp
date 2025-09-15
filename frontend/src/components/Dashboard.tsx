import React, { useState, useEffect } from 'react';
import { Droplets, Utensils, Activity, Moon, TrendingUp, Calendar, Target } from 'lucide-react';
import { habitLogApi, progressApi, feedbackApi, HabitLog, DailyProgress, Feedback } from '../services/api';

interface DashboardProps {
  userId: number;
  onViewChange: (view: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ userId, onViewChange }) => {
  const [todayLogs, setTodayLogs] = useState<HabitLog[]>([]);
  const [todayProgress, setTodayProgress] = useState<DailyProgress[]>([]);
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);

  const today = new Date().toISOString().split('T')[0];

  useEffect(() => {
    loadDashboardData();
  }, [userId]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Get today's logs
      const logsResponse = await habitLogApi.getAll(userId, { start_date: today, end_date: today });
      setTodayLogs(logsResponse.data);

      // Get progress for each habit type
      const habitTypes = ['water', 'meals', 'exercise', 'sleep'];
      const progressPromises = habitTypes.map(async (habitType) => {
        try {
          const progress = await progressApi.getDaily(userId, today, habitType);
          return progress.data;
        } catch (error) {
          return null;
        }
      });
      
      const progressResults = await Promise.all(progressPromises);
      setTodayProgress(progressResults.filter(p => p !== null));

      // Get feedback for each habit
      const feedbackPromises = habitTypes.map(async (habitType) => {
        try {
          const feedback = await feedbackApi.get(userId, habitType, 7);
          return feedback.data;
        } catch (error) {
          return null;
        }
      });
      
      const feedbackResults = await Promise.all(feedbackPromises);
      setFeedback(feedbackResults.filter(f => f !== null));
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHabitIcon = (habitType: string) => {
    switch (habitType) {
      case 'water': return Droplets;
      case 'meals': return Utensils;
      case 'exercise': return Activity;
      case 'sleep': return Moon;
      default: return Target;
    }
  };

  const getHabitColor = (habitType: string) => {
    switch (habitType) {
      case 'water': return 'text-blue-600';
      case 'meals': return 'text-green-600';
      case 'exercise': return 'text-orange-600';
      case 'sleep': return 'text-purple-600';
      default: return 'text-gray-600';
    }
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'text-success-600';
    if (percentage >= 80) return 'text-warning-600';
    return 'text-danger-600';
  };

  const getProgressBarColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-success-500';
    if (percentage >= 80) return 'bg-warning-500';
    return 'bg-danger-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mobile-container">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Today's Progress</h1>
          <p className="text-gray-600">{new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="card text-center">
            <div className="text-2xl font-bold text-primary-600">
              {todayProgress.length}
            </div>
            <div className="text-sm text-gray-600">Active Habits</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-success-600">
              {todayProgress.filter(p => p.is_goal_met).length}
            </div>
            <div className="text-sm text-gray-600">Goals Met</div>
          </div>
        </div>

        {/* Habit Progress Cards */}
        <div className="space-y-4 mb-8">
          {todayProgress.map((progress) => {
            const Icon = getHabitIcon(progress.habit_type);
            const iconColor = getHabitColor(progress.habit_type);
            const progressColor = getProgressColor(progress.completion_percentage);
            const barColor = getProgressBarColor(progress.completion_percentage);
            
            return (
              <div key={progress.habit_type} className="card">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <Icon className={`w-6 h-6 ${iconColor} mr-3`} />
                    <div>
                      <h3 className="font-semibold text-gray-800 capitalize">
                        {progress.habit_type}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {progress.logged_value.toFixed(0)} / {progress.target_value.toFixed(0)}
                      </p>
                    </div>
                  </div>
                  <div className={`text-lg font-bold ${progressColor}`}>
                    {progress.completion_percentage.toFixed(0)}%
                  </div>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${barColor}`}
                    style={{ width: `${Math.min(progress.completion_percentage, 100)}%` }}
                  />
                </div>
                
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Goal: {progress.target_value.toFixed(0)}</span>
                  <span>Streak: {progress.streak_days} days</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Recent Logs */}
        {todayLogs.length > 0 && (
          <div className="card mb-8">
            <h3 className="font-semibold text-gray-800 mb-4 flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              Today's Logs
            </h3>
            <div className="space-y-3">
              {todayLogs.map((log) => {
                const Icon = getHabitIcon(log.habit_type);
                const iconColor = getHabitColor(log.habit_type);
                
                return (
                  <div key={log.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                    <div className="flex items-center">
                      <Icon className={`w-5 h-5 ${iconColor} mr-3`} />
                      <div>
                        <p className="font-medium text-gray-800 capitalize">
                          {log.habit_type}
                        </p>
                        <p className="text-sm text-gray-600">
                          {log.logged_value} {log.unit}
                        </p>
                      </div>
                    </div>
                    <span className="text-sm text-gray-500">
                      {new Date(log.created_at).toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Feedback Section */}
        {feedback.length > 0 && (
          <div className="card mb-8">
            <h3 className="font-semibold text-gray-800 mb-4 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Your Progress
            </h3>
            <div className="space-y-4">
              {feedback.map((fb) => (
                <div key={fb.habit_type} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-800 capitalize">
                      {fb.habit_type}
                    </h4>
                    <span className="text-sm text-gray-600">
                      {fb.completion_percentage.toFixed(0)}% complete
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{fb.feedback_message}</p>
                  <p className="text-sm text-primary-600 font-medium">{fb.encouragement}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => onViewChange('tracker')}
            className="btn-primary flex items-center justify-center"
          >
            <Target className="w-5 h-5 mr-2" />
            Log Habits
          </button>
          <button
            onClick={() => onViewChange('progress')}
            className="btn-secondary flex items-center justify-center"
          >
            <TrendingUp className="w-5 h-5 mr-2" />
            View Progress
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
