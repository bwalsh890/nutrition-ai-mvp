import React, { useState, useEffect } from 'react';
import { Droplets, Utensils, Activity, Moon, Smile, Plus, Check, X } from 'lucide-react';
import { habitLogApi, habitTargetApi, HabitLog, HabitTarget } from '../services/api';

interface HabitTrackerProps {
  userId: number;
  onViewChange: (view: string) => void;
}

const HabitTracker: React.FC<HabitTrackerProps> = ({ userId, onViewChange }) => {
  const [habitTargets, setHabitTargets] = useState<HabitTarget[]>([]);
  const [todayLogs, setTodayLogs] = useState<HabitLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddLog, setShowAddLog] = useState(false);
  const [selectedHabit, setSelectedHabit] = useState<string>('');
  const [logValue, setLogValue] = useState('');
  const [logNotes, setLogNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const today = new Date().toISOString().split('T')[0];

  useEffect(() => {
    loadHabitData();
  }, [userId]);

  const loadHabitData = async () => {
    try {
      setLoading(true);
      
      // Load habit targets
      const targetsResponse = await habitTargetApi.getAll(userId);
      setHabitTargets(targetsResponse.data);

      // Load today's logs
      const logsResponse = await habitLogApi.getAll(userId, { start_date: today, end_date: today });
      setTodayLogs(logsResponse.data);
      
    } catch (error) {
      console.error('Error loading habit data:', error);
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
      case 'mood': return Smile;
      default: return Plus;
    }
  };

  const getHabitColor = (habitType: string) => {
    switch (habitType) {
      case 'water': return 'text-blue-600 bg-blue-50';
      case 'meals': return 'text-green-600 bg-green-50';
      case 'exercise': return 'text-orange-600 bg-orange-50';
      case 'sleep': return 'text-purple-600 bg-purple-50';
      case 'mood': return 'text-pink-600 bg-pink-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getTodayLogForHabit = (habitType: string) => {
    return todayLogs.find(log => log.habit_type === habitType);
  };

  const getTotalLoggedValue = (habitType: string) => {
    const logs = todayLogs.filter(log => log.habit_type === habitType);
    return logs.reduce((sum, log) => sum + log.logged_value, 0);
  };

  const handleAddLog = async () => {
    if (!selectedHabit || !logValue) return;

    try {
      setSubmitting(true);
      
      const target = habitTargets.find(t => t.habit_type === selectedHabit);
      if (!target) return;

      const logData = {
        log_date: today,
        habit_type: selectedHabit,
        logged_value: parseFloat(logValue),
        unit: target.target_unit,
        notes: logNotes || undefined
      };

      await habitLogApi.create(userId, logData);
      
      // Refresh data
      await loadHabitData();
      
      // Reset form
      setSelectedHabit('');
      setLogValue('');
      setLogNotes('');
      setShowAddLog(false);
      
    } catch (error) {
      console.error('Error adding log:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteLog = async (logId: number) => {
    try {
      const log = todayLogs.find(l => l.id === logId);
      if (!log) return;

      await habitLogApi.delete(userId, log.log_date, log.habit_type);
      await loadHabitData();
    } catch (error) {
      console.error('Error deleting log:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading habits...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mobile-container">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Habit Tracker</h1>
          <p className="text-gray-600">Log your daily habits</p>
        </div>

        {/* Habit Cards */}
        <div className="space-y-4 mb-8">
          {habitTargets.map((target) => {
            const Icon = getHabitIcon(target.habit_type);
            const colorClass = getHabitColor(target.habit_type);
            const todayLog = getTodayLogForHabit(target.habit_type);
            const totalLogged = getTotalLoggedValue(target.habit_type);
            const progress = (totalLogged / target.target_value) * 100;

            return (
              <div key={target.id} className="card">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className={`p-3 rounded-lg ${colorClass}`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <div className="ml-4">
                      <h3 className="font-semibold text-gray-800 capitalize">
                        {target.habit_type}
                      </h3>
                      <p className="text-sm text-gray-600">
                        Target: {target.target_value} {target.target_unit}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-gray-800">
                      {totalLogged.toFixed(0)}
                    </div>
                    <div className="text-sm text-gray-600">
                      {progress.toFixed(0)}%
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(progress, 100)}%` }}
                  />
                </div>

                {/* Today's Logs */}
                {todayLogs.filter(log => log.habit_type === target.habit_type).map((log) => (
                  <div key={log.id} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg mb-2">
                    <div>
                      <span className="font-medium">{log.logged_value} {log.unit}</span>
                      {log.notes && (
                        <p className="text-sm text-gray-600">{log.notes}</p>
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-500">
                        {new Date(log.created_at).toLocaleTimeString('en-US', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                      <button
                        onClick={() => handleDeleteLog(log.id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}

                {/* Add Log Button */}
                <button
                  onClick={() => {
                    setSelectedHabit(target.habit_type);
                    setShowAddLog(true);
                  }}
                  className="w-full py-2 px-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-primary-500 hover:text-primary-600 transition-colors"
                >
                  <Plus className="w-4 h-4 inline mr-2" />
                  Add {target.habit_type} log
                </button>
              </div>
            );
          })}
        </div>

        {/* Add Log Modal */}
        {showAddLog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl p-6 w-full max-w-sm">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Log {selectedHabit}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Amount
                  </label>
                  <input
                    type="number"
                    value={logValue}
                    onChange={(e) => setLogValue(e.target.value)}
                    className="input-field"
                    placeholder="Enter amount"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes (optional)
                  </label>
                  <textarea
                    value={logNotes}
                    onChange={(e) => setLogNotes(e.target.value)}
                    className="input-field"
                    rows={3}
                    placeholder="Add notes..."
                  />
                </div>
              </div>

              <div className="flex space-x-3 mt-6">
                <button
                  onClick={() => setShowAddLog(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddLog}
                  disabled={!logValue || submitting}
                  className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? 'Adding...' : 'Add Log'}
                </button>
              </div>
            </div>
          </div>
        )}

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

export default HabitTracker;
