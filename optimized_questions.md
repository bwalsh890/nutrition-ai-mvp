# Optimized Questionnaire - 15 Essential Data Points

## Question Flow Design

### 1. Hook & Motivation (3 questions)
**Q1:** "You're here to get some advice, which means potentially making some changes. What would you like to happen if I do make some recommendations and you do make some changes and everything goes really really well? What would that look like and how long would it take?"
- Data: Primary motivation, 6-month vision, timeline expectations

**Q2:** "On a scale of 1-10, how motivated do you feel to make changes right now? 1 being it feels overwhelming, 10 being you're ready to tackle anything."
- Data: Commitment level, readiness

**Q3:** "What's really going on with your health and energy right now? Be brutally honest with me."
- Data: Current energy level, main pain points

### 2. Physical Foundation (4 questions)
**Q4:** "Let's get the basics - what's your age, height, and current weight? I need this to calculate your exact nutritional needs."
- Data: Age, height, current weight

**Q5:** "What weight would help you feel the way you want to feel? And be realistic - what's actually achievable for you?"
- Data: Target weight, realistic expectations

**Q6:** "Let's talk about your relationship with exercise. What kind of activities do you currently do? And be honest - are you hitting the gym regularly, or has it been a while?"
- Data: Current exercise types, frequency, intensity

**Q7:** "I need to know your exercise history. Were you always active growing up? Maybe you played sports in school, or maybe you've never been into fitness. What's your story?"
- Data: Exercise history, past athletic background, relationship with fitness

**Q8:** "Any health conditions, medications, or allergies I need to know about? This is crucial for your safety."
- Data: Health conditions, medications, allergies

### 3. Exercise History (2 questions)
**Q9:** "What's your exercise story? Were you always active growing up, maybe played sports, or has fitness never been your thing? And what are you doing now?"
- Data: Exercise history, current activity, past athletic background

**Q10:** "When did you feel your strongest, most confident? What were you doing then, and what happened between then and now?"
- Data: Peak fitness period, what worked, decline reasons, barriers

### 4. Lifestyle Reality (4 questions)
**Q11:** "How's your relationship with food right now? What emotions come up when you think about eating?"
- Data: Emotional relationship with food, current struggles

**Q12:** "What's your cooking situation? How comfortable are you in the kitchen, and how much time do you realistically have for meal prep?"
- Data: Cooking skill level, time available

**Q13:** "What's your budget like for food? I need to know what we're working with so I can give you realistic recommendations."
- Data: Budget range, financial constraints

**Q14:** "What's your work schedule like? Do you travel, work shifts, or have a pretty regular routine?"
- Data: Work schedule, meal timing needs

### 5. Past Patterns & Obstacles (2 questions)
**Q15:** "What's worked for you before, even briefly? What made you feel amazing? And what hasn't worked?"
- Data: Past success patterns, what to avoid

**Q16:** "What gets in your way? When do you struggle most with healthy choices? Be specific."
- Data: Main obstacles, trigger situations

### 6. Support & Vision (2 questions)
**Q17:** "Who's in your corner? Who would notice if you transformed your health? And who might not be supportive?"
- Data: Support system, potential challenges

**Q18:** "Six months from now, if everything went perfectly, how would you feel? What would be different? Paint me a picture."
- Data: 6-month vision, specific outcomes

## Conversation Flow Strategy

### Opening Hook
"STOP. 🛑 Before you do anything else, I need you to know something that's going to change everything. In the next 5 minutes, I'm going to show you exactly why every diet you've ever tried has failed you. And then I'm going to give you the ONE thing that actually works. But here's the catch - I need you to be brutally honest with me. No BS. No 'I should' answers. Just the raw truth. Because here's what I know: You're tired of feeling like a failure. You're tired of starting over every Monday. You're tired of hating what you see in the mirror. And I'm about to fix ALL of that. Ready? Let's do this. 🔥"

### Transition Phrases
- "Perfect. Now I understand what's driving you."
- "I hear you. And here's what I want you to know - this is NOT your fault."
- "That's exactly why you're here. Because you're ready for something different."
- "I'm getting chills. I can literally see this happening for you."

### Closing
"Wow! 🤩 I'm genuinely impressed by everything you've shared with me. You've been so open and honest, and I can already see the amazing potential here. Let me create your personalized nutrition profile based on everything you've told me. This is going to be powerful!"

## Data Mapping to Backend
```javascript
const userProfile = {
  // Physical
  age: response.age,
  gender: response.gender || 'prefer_not_to_say',
  height_cm: response.height,
  weight_kg: response.currentWeight,
  target_weight_kg: response.targetWeight,
  activity_level: mapActivityLevel(response.exerciseFrequency, response.exerciseIntensity),
  
  // Exercise History
  current_exercise_types: response.currentExerciseTypes || [],
  exercise_frequency: response.exerciseFrequency || 0,
  exercise_intensity: response.exerciseIntensity || 'low',
  peak_fitness_period: response.peakFitnessPeriod,
  peak_fitness_activities: response.peakFitnessActivities || [],
  fitness_decline_reasons: response.fitnessDeclineReasons || [],
  years_since_peak_fitness: response.yearsSincePeakFitness || 0,
  
  // Health
  health_conditions: response.healthConditions || [],
  medications: response.medications || [],
  allergies: response.allergies || [],
  
  // Lifestyle
  cooking_skill: response.cookingSkill || 'intermediate',
  time_available: response.timeAvailable || '30_minutes',
  budget: response.budget || '400_600',
  work_schedule: response.workSchedule || 'regular',
  
  // Psychological
  primary_motivation: response.mainMotivation,
  commitment_level: response.commitmentLevel,
  current_energy_level: response.currentEnergyLevel,
  emotional_food_relationship: response.foodRelationship,
  past_success_patterns: response.pastSuccesses,
  main_obstacles: response.mainObstacles,
  support_system: response.supportSystem,
  six_month_vision: response.sixMonthVision,
  
  // Goals
  fitness_goals: extractFitnessGoals(response),
  dietary_restrictions: response.dietaryRestrictions || [],
  additional_notes: generateMissionStatement(response)
};
```

## AI Personality Adaptation
- **High commitment (8-10):** Charismatic, high energy, "Let's crush this!"
- **Medium commitment (5-7):** Supportive, encouraging, "We'll take this step by step"
- **Low commitment (1-4):** Empathetic, gentle, "We'll start small and build"
- **Young (18-25):** Use slang, high energy, "This is going to be lit!"
- **Mature (50+):** Respectful, measured, "I appreciate your wisdom"
- **Male:** "Bro, man, dude" for high intensity
- **Female:** "Girl, queen, beautiful" for high intensity
