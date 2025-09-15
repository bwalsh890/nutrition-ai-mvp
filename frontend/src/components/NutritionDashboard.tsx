import React, { useState, useEffect } from 'react';

interface NutritionTargets {
  calories: number;
  protein: number; // grams
  carbs: number;   // grams
  fat: number;     // grams
  fiber: number;   // grams
  sugar: number;   // grams
  sodium: number;  // mg
  potassium: number; // mg
  calcium: number;   // mg
  iron: number;      // mg
  vitaminC: number;  // mg
  vitaminD: number;  // mcg
  water: number;     // ml
}

interface Meal {
  id: string;
  name: string;
  time: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  sugar: number;
  sodium: number;
  potassium: number;
  calcium: number;
  iron: number;
  vitaminC: number;
  vitaminD: number;
}

interface DailyNutrition {
  targets: NutritionTargets;
  consumed: NutritionTargets;
  meals: Meal[];
  waterConsumed: number;
  waterTarget: number;
}

const NutritionDashboard: React.FC = () => {
  const [dailyNutrition, setDailyNutrition] = useState<DailyNutrition | null>(null);
  const [chatInput, setChatInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    // Initialize with sample data for demo
    initializeNutritionData();
  }, []);

  const initializeNutritionData = () => {
    // Sample data - in real app this would come from user profile and calculations
    const sampleData: DailyNutrition = {
      targets: {
        calories: 2000,
        protein: 150,
        carbs: 200,
        fat: 80,
        fiber: 25,
        sugar: 50,
        sodium: 2300,
        potassium: 3500,
        calcium: 1000,
        iron: 18,
        vitaminC: 90,
        vitaminD: 20,
        water: 2500
      },
      consumed: {
        calories: 0,
        protein: 0,
        carbs: 0,
        fat: 0,
        fiber: 0,
        sugar: 0,
        sodium: 0,
        potassium: 0,
        calcium: 0,
        iron: 0,
        vitaminC: 0,
        vitaminD: 0,
        water: 0
      },
      meals: [],
      waterConsumed: 0,
      waterTarget: 2500
    };
    setDailyNutrition(sampleData);
  };

  const parseFoodInput = (input: string): Partial<NutritionTargets> => {
    // Simple keyword-based parsing - in real app this would use USDA API
    const lowerInput = input.toLowerCase();
    const nutrition: Partial<NutritionTargets> = {};

    // Basic food parsing
    if (lowerInput.includes('chicken') || lowerInput.includes('breast')) {
      nutrition.calories = 165;
      nutrition.protein = 31;
      nutrition.fat = 3.6;
      nutrition.carbs = 0;
    }
    if (lowerInput.includes('salad') || lowerInput.includes('lettuce')) {
      nutrition.calories = 20;
      nutrition.fiber = 2;
      nutrition.vitaminC = 15;
    }
    if (lowerInput.includes('rice') || lowerInput.includes('brown rice')) {
      nutrition.calories = 220;
      nutrition.carbs = 45;
      nutrition.protein = 5;
      nutrition.fiber = 3.5;
    }
    if (lowerInput.includes('avocado')) {
      nutrition.calories = 160;
      nutrition.fat = 15;
      nutrition.fiber = 7;
      nutrition.potassium = 485;
    }
    if (lowerInput.includes('water')) {
      const waterMatch = input.match(/(\d+)/);
      if (waterMatch) {
        nutrition.water = parseInt(waterMatch[1]);
      }
    }

    return nutrition;
  };

  const handleChatSubmit = async () => {
    if (!chatInput.trim() || !dailyNutrition) return;

    setIsProcessing(true);
    
    // Parse the food input
    const parsedNutrition = parseFoodInput(chatInput);
    
    // Add to consumed amounts
    const newConsumed = { ...dailyNutrition.consumed };
    Object.keys(parsedNutrition).forEach(key => {
      if (parsedNutrition[key as keyof NutritionTargets]) {
        newConsumed[key as keyof NutritionTargets] += parsedNutrition[key as keyof NutritionTargets]!;
      }
    });

    // Create meal entry
    const newMeal: Meal = {
      id: Date.now().toString(),
      name: chatInput,
      time: new Date().toLocaleTimeString(),
      calories: parsedNutrition.calories || 0,
      protein: parsedNutrition.protein || 0,
      carbs: parsedNutrition.carbs || 0,
      fat: parsedNutrition.fat || 0,
      fiber: parsedNutrition.fiber || 0,
      sugar: parsedNutrition.sugar || 0,
      sodium: parsedNutrition.sodium || 0,
      potassium: parsedNutrition.potassium || 0,
      calcium: parsedNutrition.calcium || 0,
      iron: parsedNutrition.iron || 0,
      vitaminC: parsedNutrition.vitaminC || 0,
      vitaminD: parsedNutrition.vitaminD || 0
    };

    setDailyNutrition(prev => ({
      ...prev!,
      consumed: newConsumed,
      meals: [...prev!.meals, newMeal],
      waterConsumed: newConsumed.water
    }));

    setChatInput('');
    setIsProcessing(false);
  };

  const getProgressPercentage = (consumed: number, target: number): number => {
    return Math.min((consumed / target) * 100, 100);
  };

  const getProgressColor = (percentage: number): string => {
    if (percentage >= 100) return 'bg-green-500';
    if (percentage >= 75) return 'bg-yellow-500';
    if (percentage >= 50) return 'bg-orange-500';
    return 'bg-red-500';
  };

  if (!dailyNutrition) {
    return <div className="p-4">Loading nutrition data...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Today's Nutrition Plan</h1>
          <p className="text-gray-600">Track your daily nutrition goals and progress</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl font-bold text-blue-600">{dailyNutrition.consumed.calories}</div>
            <div className="text-sm text-gray-600">of {dailyNutrition.targets.calories} calories</div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className={`h-2 rounded-full ${getProgressColor(getProgressPercentage(dailyNutrition.consumed.calories, dailyNutrition.targets.calories))}`}
                style={{ width: `${getProgressPercentage(dailyNutrition.consumed.calories, dailyNutrition.targets.calories)}%` }}
              />
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl font-bold text-green-600">{dailyNutrition.consumed.protein}g</div>
            <div className="text-sm text-gray-600">of {dailyNutrition.targets.protein}g protein</div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className={`h-2 rounded-full ${getProgressColor(getProgressPercentage(dailyNutrition.consumed.protein, dailyNutrition.targets.protein))}`}
                style={{ width: `${getProgressPercentage(dailyNutrition.consumed.protein, dailyNutrition.targets.protein)}%` }}
              />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl font-bold text-yellow-600">{dailyNutrition.consumed.carbs}g</div>
            <div className="text-sm text-gray-600">of {dailyNutrition.targets.carbs}g carbs</div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className={`h-2 rounded-full ${getProgressColor(getProgressPercentage(dailyNutrition.consumed.carbs, dailyNutrition.targets.carbs))}`}
                style={{ width: `${getProgressPercentage(dailyNutrition.consumed.carbs, dailyNutrition.targets.carbs)}%` }}
              />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl font-bold text-purple-600">{dailyNutrition.consumed.fat}g</div>
            <div className="text-sm text-gray-600">of {dailyNutrition.targets.fat}g fat</div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className={`h-2 rounded-full ${getProgressColor(getProgressPercentage(dailyNutrition.consumed.fat, dailyNutrition.targets.fat))}`}
                style={{ width: `${getProgressPercentage(dailyNutrition.consumed.fat, dailyNutrition.targets.fat)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Chat Input */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Log Your Food</h2>
          <div className="flex space-x-3">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleChatSubmit()}
              placeholder="What did you eat? (e.g., 'chicken breast with rice and salad')"
              className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isProcessing}
            />
            <button
              onClick={handleChatSubmit}
              disabled={!chatInput.trim() || isProcessing}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isProcessing ? 'Processing...' : 'Log Food'}
            </button>
          </div>
        </div>

        {/* Detailed Nutrition Breakdown */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Macros */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Macronutrients</h3>
            <div className="space-y-4">
              {[
                { name: 'Protein', consumed: dailyNutrition.consumed.protein, target: dailyNutrition.targets.protein, unit: 'g', color: 'green' },
                { name: 'Carbs', consumed: dailyNutrition.consumed.carbs, target: dailyNutrition.targets.carbs, unit: 'g', color: 'yellow' },
                { name: 'Fat', consumed: dailyNutrition.consumed.fat, target: dailyNutrition.targets.fat, unit: 'g', color: 'purple' },
                { name: 'Fiber', consumed: dailyNutrition.consumed.fiber, target: dailyNutrition.targets.fiber, unit: 'g', color: 'blue' }
              ].map((macro) => (
                <div key={macro.name} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">{macro.name}</span>
                    <span className="font-medium">{macro.consumed}{macro.unit} / {macro.target}{macro.unit}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full bg-${macro.color}-500`}
                      style={{ width: `${getProgressPercentage(macro.consumed, macro.target)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Micronutrients */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Micronutrients</h3>
            <div className="space-y-4">
              {[
                { name: 'Sodium', consumed: dailyNutrition.consumed.sodium, target: dailyNutrition.targets.sodium, unit: 'mg' },
                { name: 'Potassium', consumed: dailyNutrition.consumed.potassium, target: dailyNutrition.targets.potassium, unit: 'mg' },
                { name: 'Calcium', consumed: dailyNutrition.consumed.calcium, target: dailyNutrition.targets.calcium, unit: 'mg' },
                { name: 'Iron', consumed: dailyNutrition.consumed.iron, target: dailyNutrition.targets.iron, unit: 'mg' },
                { name: 'Vitamin C', consumed: dailyNutrition.consumed.vitaminC, target: dailyNutrition.targets.vitaminC, unit: 'mg' },
                { name: 'Vitamin D', consumed: dailyNutrition.consumed.vitaminD, target: dailyNutrition.targets.vitaminD, unit: 'mcg' }
              ].map((micro) => (
                <div key={micro.name} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">{micro.name}</span>
                    <span className="font-medium">{micro.consumed}{micro.unit} / {micro.target}{micro.unit}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full bg-blue-500"
                      style={{ width: `${getProgressPercentage(micro.consumed, micro.target)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Water Tracking */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Hydration</h3>
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Water</span>
                <span className="font-medium">{dailyNutrition.waterConsumed}ml / {dailyNutrition.waterTarget}ml</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="h-3 rounded-full bg-blue-500"
                  style={{ width: `${getProgressPercentage(dailyNutrition.waterConsumed, dailyNutrition.waterTarget)}%` }}
                />
              </div>
            </div>
            <button className="bg-blue-100 text-blue-600 px-4 py-2 rounded-lg font-medium hover:bg-blue-200 transition-colors">
              +250ml
            </button>
          </div>
        </div>

        {/* Meals Today */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Meals Today</h3>
          {dailyNutrition.meals.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No meals logged yet. Start by logging your first meal above!</p>
          ) : (
            <div className="space-y-3">
              {dailyNutrition.meals.map((meal) => (
                <div key={meal.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-medium text-gray-900">{meal.name}</h4>
                      <p className="text-sm text-gray-500">{meal.time}</p>
                    </div>
                    <span className="text-sm font-medium text-gray-600">{meal.calories} cal</span>
                  </div>
                  <div className="grid grid-cols-4 gap-2 text-xs text-gray-600">
                    <div>P: {meal.protein}g</div>
                    <div>C: {meal.carbs}g</div>
                    <div>F: {meal.fat}g</div>
                    <div>Fiber: {meal.fiber}g</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NutritionDashboard;
