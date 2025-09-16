import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { userApi, questionnaireApi, habitTargetApi } from './services/api';
import Questionnaire from './components/Questionnaire';
import HabitTracker from './components/HabitTracker';
import Progress from './components/Progress';
import Navigation from './components/Navigation';
import LoadingSpinner from './components/LoadingSpinner';
import OnboardingChat from './components/OnboardingChat';
import NutritionDashboard from './components/NutritionDashboard';

const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [hasQuestionnaire, setHasQuestionnaire] = useState(false);
  const [hasHabitTargets, setHasHabitTargets] = useState(false);
  const [loading, setLoading] = useState(true);
  const [currentView, setCurrentView] = useState('questionnaire');

  // Initialize app with a demo user
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      setLoading(true);
      
      // Create or get a demo user
      let user;
      try {
        const users = await userApi.getAll();
        if (users.data.length > 0) {
          user = users.data[0];
        } else {
          // Create a demo user
          const newUser = await userApi.create({
            email: 'demo@example.com',
            username: 'demo_user',
            full_name: 'Demo User',
            password: 'demo123'
          });
          user = newUser.data;
        }
      } catch (error) {
        console.error('Error creating/getting user:', error);
        // Create a mock user for demo
        user = {
          id: 1,
          email: 'demo@example.com',
          username: 'demo_user',
          full_name: 'Demo User'
        };
      }

      setCurrentUser(user);

      // Check if user has questionnaire
      try {
        const questionnaire = await questionnaireApi.get(user.id);
        setHasQuestionnaire(true);
        
        // Check if user has habit targets
        const targets = await habitTargetApi.getAll(user.id);
        setHasHabitTargets(targets.data.length > 0);
        
        if (targets.data.length > 0) {
          setCurrentView('dashboard');
        }
      } catch (error) {
        console.log('No questionnaire found, starting with questionnaire');
        setHasQuestionnaire(false);
        setHasHabitTargets(false);
      }
    } catch (error) {
      console.error('Error initializing app:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionnaireComplete = async (questionnaireData: any) => {
    if (!currentUser) return;
    
    try {
      await questionnaireApi.create(currentUser.id, questionnaireData);
      setHasQuestionnaire(true);
      
      // Generate habit targets based on questionnaire
      const targets = generateHabitTargets(questionnaireData);
      for (const target of targets) {
        await habitTargetApi.create(currentUser.id, target);
      }
      
      setHasHabitTargets(true);
      setCurrentView('dashboard');
    } catch (error) {
      console.error('Error saving questionnaire:', error);
    }
  };

  const generateHabitTargets = (questionnaire: any) => {
    const targets = [];
    
    if (questionnaire.water_goal_ml) {
      targets.push({
        habit_type: 'water',
        target_value: questionnaire.water_goal_ml,
        target_unit: 'ml',
        is_active: true
      });
    }
    
    if (questionnaire.meal_frequency) {
      targets.push({
        habit_type: 'meals',
        target_value: questionnaire.meal_frequency,
        target_unit: 'count',
        is_active: true
      });
    }
    
    if (questionnaire.exercise_frequency && questionnaire.exercise_duration) {
      targets.push({
        habit_type: 'exercise',
        target_value: questionnaire.exercise_frequency * questionnaire.exercise_duration,
        target_unit: 'minutes',
        is_active: true
      });
    }
    
    if (questionnaire.sleep_hours) {
      targets.push({
        habit_type: 'sleep',
        target_value: questionnaire.sleep_hours,
        target_unit: 'hours',
        is_active: true
      });
    }
    
    return targets;
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!currentUser) {
    return (
      <div className="mobile-container flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">Welcome to Nutrition AI</h1>
          <p className="text-gray-600">Loading your profile...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="mobile-container">
        <Routes>
          <Route path="/onboarding" element={<OnboardingChat />} />
          <Route path="/nutrition" element={<NutritionDashboard />} />
          <Route path="/" element={
            !hasQuestionnaire ? (
              <Navigate to="/onboarding" replace />
            ) : currentView === 'dashboard' ? (
              <NutritionDashboard />
            ) : currentView === 'tracker' ? (
              <HabitTracker userId={currentUser.id} onViewChange={setCurrentView} />
            ) : currentView === 'progress' ? (
              <Progress userId={currentUser.id} onViewChange={setCurrentView} />
            ) : (
              <Questionnaire onComplete={handleQuestionnaireComplete} />
            )
          } />
        </Routes>
        
        {hasQuestionnaire && (
          <Navigation currentView={currentView} onViewChange={setCurrentView} />
        )}
      </div>
    </Router>
  );
};

export default App;
