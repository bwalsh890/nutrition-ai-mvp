# Final Data Points - 18 Essential Outputs

## Core Personal Data (5 points)
1. **Age** - For metabolic rate, nutrient needs, life stage considerations
2. **Gender** - For hormonal considerations, body composition targets  
3. **Height** - For BMI calculations, portion sizing
4. **Current Weight** - For caloric needs, progress tracking
5. **Target Weight** - For goal setting, timeline planning

## Health & Safety (3 points)
6. **Health Conditions** - Diabetes, heart disease, PCOS, etc.
7. **Medications** - Drug-nutrient interactions
8. **Allergies** - Life-threatening vs. preferences

## Exercise & Activity (4 points)
9. **Current Exercise Types** - What they're doing now (gym, running, walking, nothing)
10. **Exercise Frequency** - How often per week
11. **Exercise History** - Always active vs. never been into fitness
12. **Peak Fitness Period** - When they felt strongest, what worked, what happened

## Lifestyle & Practical (3 points)
13. **Cooking Skill Level** - For recipe complexity, prep time
14. **Time Available for Cooking** - For meal planning, batch cooking
15. **Budget Range** - For ingredient selection, meal planning

## Psychological & Motivational (3 points)
16. **Primary Motivation** - Why this matters (energy, confidence, health, etc.)
17. **Current Energy Level** - Baseline state (1-10 scale)
18. **6-Month Vision** - Specific, measurable outcomes they want

## Total: 18 Data Points

### Data Mapping to Backend
```javascript
const userProfile = {
  // Physical (5)
  age: response.age,
  gender: response.gender || 'prefer_not_to_say',
  height_cm: response.height,
  weight_kg: response.currentWeight,
  target_weight_kg: response.targetWeight,
  
  // Health & Safety (3)
  health_conditions: response.healthConditions || [],
  medications: response.medications || [],
  allergies: response.allergies || [],
  
  // Exercise & Activity (4)
  current_exercise_types: response.currentExerciseTypes || [],
  exercise_frequency: response.exerciseFrequency || 0,
  exercise_history: response.exerciseHistory, // 'always_active', 'never_active', 'former_athlete'
  peak_fitness_period: response.peakFitnessPeriod,
  peak_fitness_activities: response.peakFitnessActivities || [],
  fitness_decline_reasons: response.fitnessDeclineReasons || [],
  
  // Lifestyle & Practical (3)
  cooking_skill: response.cookingSkill || 'intermediate',
  time_available: response.timeAvailable || '30_minutes',
  budget: response.budget || '400_600',
  
  // Psychological & Motivational (3)
  primary_motivation: response.mainMotivation,
  current_energy_level: response.currentEnergyLevel,
  six_month_vision: response.sixMonthVision,
  
  // Calculated Fields
  activity_level: mapActivityLevel(response.exerciseFrequency, response.exerciseIntensity),
  fitness_goals: extractFitnessGoals(response),
  dietary_restrictions: response.dietaryRestrictions || [],
  additional_notes: generateMissionStatement(response)
};
```

### Question Flow (18 questions total)
1. Hook & Motivation (3 questions)
2. Physical Foundation (5 questions) 
3. Health & Safety (3 questions)
4. Exercise History (2 questions)
5. Lifestyle Reality (3 questions)
6. Vision & Goals (2 questions)

**This gives us everything we need for true personalization while keeping it conversational and engaging.**
