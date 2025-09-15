import React, { useState } from 'react';
import { User, Heart, Droplets, Utensils, Activity, Moon, Target } from 'lucide-react';

interface QuestionnaireProps {
  onComplete: (data: any) => void;
}

const Questionnaire: React.FC<QuestionnaireProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    sleep_hours: 8,
    water_goal_ml: 2000,
    meal_frequency: 3,
    exercise_frequency: 3,
    exercise_duration: 30,
    stress_level: 'moderate',
    energy_level: 'moderate',
    mood_tracking: false,
    weight_goal: 'maintain',
    target_weight_kg: 70
  });

  const steps = [
    { title: 'Sleep Habits', icon: Moon },
    { title: 'Hydration Goals', icon: Droplets },
    { title: 'Meal Planning', icon: Utensils },
    { title: 'Exercise Routine', icon: Activity },
    { title: 'Health & Wellness', icon: Heart },
    { title: 'Goals & Tracking', icon: Target }
  ];

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete(formData);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // Sleep
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Moon className="w-12 h-12 text-primary-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-800 mb-2">Sleep Habits</h2>
              <p className="text-gray-600">Tell us about your sleep patterns</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                How many hours do you sleep per night?
              </label>
              <input
                type="number"
                min="4"
                max="12"
                step="0.5"
                value={formData.sleep_hours}
                onChange={(e) => handleInputChange('sleep_hours', parseFloat(e.target.value))}
                className="input-field"
              />
            </div>
          </div>
        );

      case 1: // Water
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Droplets className="w-12 h-12 text-primary-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-800 mb-2">Hydration Goals</h2>
              <p className="text-gray-600">Set your daily water intake target</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Daily water goal (ml)
              </label>
              <input
                type="number"
                min="500"
                max="5000"
                step="100"
                value={formData.water_goal_ml}
                onChange={(e) => handleInputChange('water_goal_ml', parseInt(e.target.value))}
                className="input-field"
              />
              <p className="text-sm text-gray-500 mt-1">
                Recommended: 2000-3000ml per day
              </p>
            </div>
          </div>
        );

      case 2: // Meals
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Utensils className="w-12 h-12 text-primary-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-800 mb-2">Meal Planning</h2>
              <p className="text-gray-600">How often do you eat?</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Meals per day
              </label>
              <input
                type="number"
                min="1"
                max="6"
                value={formData.meal_frequency}
                onChange={(e) => handleInputChange('meal_frequency', parseInt(e.target.value))}
                className="input-field"
              />
            </div>
          </div>
        );

      case 3: // Exercise
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Activity className="w-12 h-12 text-primary-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-800 mb-2">Exercise Routine</h2>
              <p className="text-gray-600">Tell us about your fitness habits</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Exercise days per week
              </label>
              <input
                type="number"
                min="0"
                max="7"
                value={formData.exercise_frequency}
                onChange={(e) => handleInputChange('exercise_frequency', parseInt(e.target.value))}
                className="input-field"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration per session (minutes)
              </label>
              <input
                type="number"
                min="5"
                max="180"
                step="5"
                value={formData.exercise_duration}
                onChange={(e) => handleInputChange('exercise_duration', parseInt(e.target.value))}
                className="input-field"
              />
            </div>
          </div>
        );

      case 4: // Health
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Heart className="w-12 h-12 text-primary-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-800 mb-2">Health & Wellness</h2>
              <p className="text-gray-600">Help us understand your current state</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Current stress level
              </label>
              <select
                value={formData.stress_level}
                onChange={(e) => handleInputChange('stress_level', e.target.value)}
                className="input-field"
              >
                <option value="low">Low</option>
                <option value="moderate">Moderate</option>
                <option value="high">High</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Energy level
              </label>
              <select
                value={formData.energy_level}
                onChange={(e) => handleInputChange('energy_level', e.target.value)}
                className="input-field"
              >
                <option value="low">Low</option>
                <option value="moderate">Moderate</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
        );

      case 5: // Goals
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Target className="w-12 h-12 text-primary-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-800 mb-2">Goals & Tracking</h2>
              <p className="text-gray-600">Set your personal goals</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Weight goal
              </label>
              <select
                value={formData.weight_goal}
                onChange={(e) => handleInputChange('weight_goal', e.target.value)}
                className="input-field"
              >
                <option value="lose">Lose weight</option>
                <option value="maintain">Maintain weight</option>
                <option value="gain">Gain weight</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target weight (kg)
              </label>
              <input
                type="number"
                min="30"
                max="200"
                step="0.1"
                value={formData.target_weight_kg}
                onChange={(e) => handleInputChange('target_weight_kg', parseFloat(e.target.value))}
                className="input-field"
              />
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="mood_tracking"
                checked={formData.mood_tracking}
                onChange={(e) => handleInputChange('mood_tracking', e.target.checked)}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="mood_tracking" className="ml-2 block text-sm text-gray-700">
                Enable mood tracking
              </label>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mobile-container">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Step {currentStep + 1} of {steps.length}</span>
            <span>{Math.round(((currentStep + 1) / steps.length) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="card mb-8">
          {renderStepContent()}
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className={`btn-secondary ${currentStep === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            Previous
          </button>
          
          <button
            onClick={handleNext}
            className="btn-primary"
          >
            {currentStep === steps.length - 1 ? 'Complete Setup' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Questionnaire;
