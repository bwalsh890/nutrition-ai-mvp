import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { TrendingUp, Calendar, ArrowLeft, ArrowRight } from 'lucide-react';
import { progressApi, habitTargetApi, DailyProgress, WeeklyProgress, MonthlyProgress, HabitTarget } from '../services/api';

interface ProgressProps {
  userId: number;
  onViewChange: (view: string) => void;
}

const Progress: React.FC<ProgressProps> = ({ userId, onViewChange }) => {
  const [habitTargets, setHabitTargets] = useState<HabitTarget[]>([]);
  const [selectedHabit, setSelectedHabit] = useState<string>('');
  const [timeRange, setTimeRange] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [progressData, setProgressData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    loadHabitTargets();
  }, [userId]);

  useEffect(() => {
    if (selectedHabit) {
      loadProgressData();
    }
  }, [selectedHabit, timeRange, currentDate]);

  const loadHabitTargets = async () => {
    try {
      const response = await habitTargetApi.getAll(userId);
      setHabitTargets(response.data);
      if (response.data.length > 0) {
        setSelectedHabit(response.data[0].habit_type);
      }
    } catch (error) {
      console.error('Error loading habit targets:', error);
    }
  };

  const loadProgressData = async () => {
    if (!selectedHabit) return;

    try {
      setLoading(true);
      let data: any[] = [];

      if (timeRange === 'daily') {
        // Get last 7 days
        for (let i = 6; i >= 0; i--) {
          const date = new Date(currentDate);
          date.setDate(date.getDate() - i);
          const dateStr = date.toISOString().split('T')[0];
          
          try {
            const response = await progressApi.getDaily(userId, dateStr, selectedHabit);
            data.push({
              date: dateStr,
              day: date.toLocaleDateString('en-US', { weekday: 'short' }),
              completion: response.data.completion_percentage,
              logged: response.data.logged_value,
              target: response.data.target_value,
              goalMet: response.data.is_goal_met
            });
          } catch (error) {
            data.push({
              date: dateStr,
              day: date.toLocaleDateString('en-US', { weekday: 'short' }),
              completion: 0,
              logged: 0,
              target: 0,
              goalMet: false
            });
          }
        }
      } else if (timeRange === 'weekly') {
        // Get last 4 weeks
        for (let i = 3; i >= 0; i--) {
          const weekStart = new Date(currentDate);
          weekStart.setDate(weekStart.getDate() - (weekStart.getDay() + (i * 7)));
          const weekStartStr = weekStart.toISOString().split('T')[0];
          
          try {
            const response = await progressApi.getWeekly(userId, weekStartStr, selectedHabit);
            data.push({
              week: `Week ${4 - i}`,
              weekStart: weekStartStr,
              completion: response.data.completion_percentage,
              total: response.data.total_value,
              target: response.data.target_value,
              daysMet: response.data.days_met
            });
          } catch (error) {
            data.push({
              week: `Week ${4 - i}`,
              weekStart: weekStartStr,
              completion: 0,
              total: 0,
              target: 0,
              daysMet: 0
            });
          }
        }
      } else if (timeRange === 'monthly') {
        // Get last 6 months
        for (let i = 5; i >= 0; i--) {
          const month = new Date(currentDate);
          month.setMonth(month.getMonth() - i);
          const year = month.getFullYear();
          const monthNum = month.getMonth() + 1;
          
          try {
            const response = await progressApi.getMonthly(userId, year, monthNum, selectedHabit);
            data.push({
              month: month.toLocaleDateString('en-US', { month: 'short' }),
              year: year,
              completion: response.data.completion_percentage,
              total: response.data.total_value,
              target: response.data.target_value,
              daysMet: response.data.days_met
            });
          } catch (error) {
            data.push({
              month: month.toLocaleDateString('en-US', { month: 'short' }),
              year: year,
              completion: 0,
              total: 0,
              target: 0,
              daysMet: 0
            });
          }
        }
      }

      setProgressData(data);
    } catch (error) {
      console.error('Error loading progress data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHabitColor = (habitType: string) => {
    switch (habitType) {
      case 'water': return '#3b82f6';
      case 'meals': return '#10b981';
      case 'exercise': return '#f59e0b';
      case 'sleep': return '#8b5cf6';
      case 'mood': return '#ec4899';
      default: return '#6b7280';
    }
  };

  const formatTooltip = (value: any, name: string) => {
    if (name === 'completion') return [`${value.toFixed(1)}%`, 'Completion'];
    if (name === 'logged') return [`${value.toFixed(0)}`, 'Logged'];
    if (name === 'total') return [`${value.toFixed(0)}`, 'Total'];
    if (name === 'target') return [`${value.toFixed(0)}`, 'Target'];
    if (name === 'daysMet') return [`${value}`, 'Days Met'];
    return [value, name];
  };

  const getAverageCompletion = () => {
    if (progressData.length === 0) return 0;
    const sum = progressData.reduce((acc, item) => acc + item.completion, 0);
    return sum / progressData.length;
  };

  const getGoalMetDays = () => {
    return progressData.filter(item => item.goalMet || item.completion >= 100).length;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading progress...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mobile-container">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Progress Tracking</h1>
          <p className="text-gray-600">Monitor your habit progress over time</p>
        </div>

        {/* Controls */}
        <div className="card mb-6">
          <div className="space-y-4">
            {/* Habit Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Habit
              </label>
              <select
                value={selectedHabit}
                onChange={(e) => setSelectedHabit(e.target.value)}
                className="input-field"
              >
                {habitTargets.map((target) => (
                  <option key={target.id} value={target.habit_type}>
                    {target.habit_type.charAt(0).toUpperCase() + target.habit_type.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Time Range Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Range
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['daily', 'weekly', 'monthly'] as const).map((range) => (
                  <button
                    key={range}
                    onClick={() => setTimeRange(range)}
                    className={`py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                      timeRange === range
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {range.charAt(0).toUpperCase() + range.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="card text-center">
            <div className="text-2xl font-bold text-primary-600">
              {getAverageCompletion().toFixed(0)}%
            </div>
            <div className="text-sm text-gray-600">Avg Completion</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-success-600">
              {getGoalMetDays()}
            </div>
            <div className="text-sm text-gray-600">Goal Met Days</div>
          </div>
        </div>

        {/* Chart */}
        <div className="card mb-6">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2" />
            Progress Chart
          </h3>
          
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              {timeRange === 'daily' ? (
                <LineChart data={progressData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="day" 
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis 
                    domain={[0, 100]}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip formatter={formatTooltip} />
                  <Line
                    type="monotone"
                    dataKey="completion"
                    stroke={getHabitColor(selectedHabit)}
                    strokeWidth={3}
                    dot={{ fill: getHabitColor(selectedHabit), strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              ) : (
                <BarChart data={progressData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey={timeRange === 'weekly' ? 'week' : 'month'}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis 
                    domain={[0, 100]}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip formatter={formatTooltip} />
                  <Bar
                    dataKey="completion"
                    fill={getHabitColor(selectedHabit)}
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              )}
            </ResponsiveContainer>
          </div>
        </div>

        {/* Detailed Data Table */}
        <div className="card mb-8">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center">
            <Calendar className="w-5 h-5 mr-2" />
            Detailed Data
          </h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 font-medium text-gray-700">
                    {timeRange === 'daily' ? 'Day' : timeRange === 'weekly' ? 'Week' : 'Month'}
                  </th>
                  <th className="text-right py-2 font-medium text-gray-700">Completion</th>
                  <th className="text-right py-2 font-medium text-gray-700">
                    {timeRange === 'daily' ? 'Logged' : 'Total'}
                  </th>
                  <th className="text-right py-2 font-medium text-gray-700">Target</th>
                </tr>
              </thead>
              <tbody>
                {progressData.map((item, index) => (
                  <tr key={index} className="border-b border-gray-100">
                    <td className="py-2 text-gray-800">
                      {timeRange === 'daily' ? item.day : 
                       timeRange === 'weekly' ? item.week : 
                       `${item.month} ${item.year}`}
                    </td>
                    <td className="text-right py-2">
                      <span className={`font-medium ${
                        item.completion >= 100 ? 'text-success-600' :
                        item.completion >= 80 ? 'text-warning-600' :
                        'text-danger-600'
                      }`}>
                        {item.completion.toFixed(0)}%
                      </span>
                    </td>
                    <td className="text-right py-2 text-gray-600">
                      {timeRange === 'daily' ? item.logged.toFixed(0) : item.total.toFixed(0)}
                    </td>
                    <td className="text-right py-2 text-gray-600">
                      {item.target.toFixed(0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Back Button */}
        <button
          onClick={() => onViewChange('dashboard')}
          className="w-full btn-secondary"
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );
};

export default Progress;
