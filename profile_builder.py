from typing import Dict, List, Optional
import re
from datetime import datetime

class UserProfileBuilder:
    def __init__(self):
        self.profile_template = {
            # Basic Demographics
            "age_range": None,
            "gender": None,
            "height_cm": None,
            "weight_kg": None,
            "bmi": None,
            "target_weight_kg": None,
            
            # Discovery & Motivation
            "discovery_method": None,
            "discovery_reason": None,
            "initial_motivation": None,
            "motivation_strength": None,  # high/medium/low based on language
            
            # Goals & Vision
            "primary_goals": [],  # extracted from hopes_goals
            "secondary_goals": [],
            "ideal_vision": None,
            "current_obstacles": [],
            "obstacle_severity": None,  # high/medium/low
            
            # Current State
            "current_activity_level": None,  # sedentary/light/moderate/active/very_active
            "current_energy_level": None,  # low/medium/high
            "current_diet_quality": None,  # poor/fair/good/excellent
            "current_diet_details": None,
            
            # Psychological Profile
            "motivation_type": None,  # intrinsic/extrinsic/mixed
            "confidence_level": None,  # low/medium/high
            "support_level": None,  # low/medium/high
            "urgency_level": None,  # low/medium/high
            
            # Dietary Preferences & Restrictions
            "dietary_restrictions": [],
            "food_preferences": [],
            "cooking_skill": None,  # beginner/intermediate/advanced
            "meal_prep_willingness": None,  # low/medium/high
            
            # Lifestyle Factors
            "time_availability": None,  # low/medium/high
            "budget_constraints": None,  # low/medium/high
            "social_eating_patterns": None,
            "work_schedule_impact": None,
            
            # Health Considerations
            "health_conditions": [],
            "medications": [],
            "allergies": [],
            "energy_patterns": None,  # morning/afternoon/evening person
            
            # Behavioral Patterns
            "eating_triggers": [],
            "stress_eating": None,  # yes/no/sometimes
            "emotional_eating": None,  # yes/no/sometimes
            "meal_skipping": None,  # yes/no/sometimes
            
            # Success Factors
            "past_successes": [],
            "learning_style": None,  # visual/auditory/kinesthetic
            "accountability_preference": None,  # self/partner/group/coach
            "feedback_frequency": None,  # daily/weekly/monthly
        }
    
    def build_profile(self, onboarding_responses: Dict) -> Dict:
        """Build comprehensive user profile from onboarding responses"""
        profile = self.profile_template.copy()
        
        # Extract basic info from responses
        self._extract_basic_demographics(profile, onboarding_responses)
        self._extract_motivation_profile(profile, onboarding_responses)
        self._extract_goals_and_vision(profile, onboarding_responses)
        self._extract_current_state(profile, onboarding_responses)
        self._extract_psychological_profile(profile, onboarding_responses)
        self._extract_dietary_preferences(profile, onboarding_responses)
        self._extract_lifestyle_factors(profile, onboarding_responses)
        self._extract_health_considerations(profile, onboarding_responses)
        self._extract_behavioral_patterns(profile, onboarding_responses)
        self._extract_success_factors(profile, onboarding_responses)
        
        # Calculate derived metrics
        self._calculate_derived_metrics(profile)
        
        return profile
    
    def _extract_basic_demographics(self, profile: Dict, responses: Dict):
        """Extract age, gender, height, weight from responses"""
        basic_measurements = responses.get("basic_measurements", "").lower()
        
        # Extract height
        height_match = re.search(r'(\d+)\s*(?:cm|centimeters?|inches?|ft|feet)', basic_measurements)
        if height_match:
            height = int(height_match.group(1))
            if 'inch' in basic_measurements or 'ft' in basic_measurements:
                profile["height_cm"] = height * 2.54  # Convert inches to cm
            else:
                profile["height_cm"] = height
        
        # Extract weight
        weight_match = re.search(r'(\d+)\s*(?:kg|kilos?|pounds?|lbs?)', basic_measurements)
        if weight_match:
            weight = int(weight_match.group(1))
            if 'pound' in basic_measurements or 'lb' in basic_measurements:
                profile["weight_kg"] = weight * 0.453592  # Convert lbs to kg
            else:
                profile["weight_kg"] = weight
        
        # Extract energy level
        if any(word in basic_measurements for word in ['tired', 'exhausted', 'drained', 'low']):
            profile["current_energy_level"] = "low"
        elif any(word in basic_measurements for word in ['good', 'okay', 'fine', 'medium']):
            profile["current_energy_level"] = "medium"
        elif any(word in basic_measurements for word in ['high', 'great', 'energetic', 'amazing']):
            profile["current_energy_level"] = "high"
    
    def _extract_motivation_profile(self, profile: Dict, responses: Dict):
        """Extract motivation patterns and strength"""
        discovery_method = responses.get("discovery_method", "").lower()
        initial_motivation = responses.get("initial_motivation", "").lower()
        
        # Discovery method
        if any(word in discovery_method for word in ['instagram', 'social', 'facebook', 'tiktok']):
            profile["discovery_method"] = "social_media"
        elif any(word in discovery_method for word in ['google', 'search', 'online']):
            profile["discovery_method"] = "search"
        elif any(word in discovery_method for word in ['friend', 'recommend', 'referral']):
            profile["discovery_method"] = "referral"
        else:
            profile["discovery_method"] = "other"
        
        # Motivation strength
        motivation_text = initial_motivation
        urgent_words = ['urgent', 'desperate', 'need', 'must', 'critical', 'important']
        strong_words = ['determined', 'committed', 'serious', 'ready', 'focused']
        
        if any(word in motivation_text for word in urgent_words):
            profile["motivation_strength"] = "high"
        elif any(word in motivation_text for word in strong_words):
            profile["motivation_strength"] = "medium"
        else:
            profile["motivation_strength"] = "low"
        
        # Motivation type
        if any(word in motivation_text for word in ['feel', 'want', 'desire', 'passion']):
            profile["motivation_type"] = "intrinsic"
        elif any(word in motivation_text for word in ['doctor', 'family', 'partner', 'should']):
            profile["motivation_type"] = "extrinsic"
        else:
            profile["motivation_type"] = "mixed"
    
    def _extract_goals_and_vision(self, profile: Dict, responses: Dict):
        """Extract goals and vision from responses"""
        hopes_goals = responses.get("hopes_goals", "").lower()
        ideal_vision = responses.get("ideal_vision", "").lower()
        obstacles = responses.get("main_obstacles", "").lower()
        
        # Extract primary goals
        goal_keywords = {
            'weight_loss': ['lose weight', 'slim', 'skinny', 'thin', 'weight'],
            'muscle_gain': ['muscle', 'strong', 'toned', 'build', 'gains'],
            'energy': ['energy', 'tired', 'exhausted', 'vitality', 'alive'],
            'health': ['healthy', 'health', 'wellness', 'medical'],
            'confidence': ['confident', 'confidence', 'self-esteem', 'proud'],
            'performance': ['perform', 'athletic', 'fitness', 'endurance']
        }
        
        for goal, keywords in goal_keywords.items():
            if any(keyword in hopes_goals for keyword in keywords):
                profile["primary_goals"].append(goal)
        
        # Extract obstacles and severity
        obstacle_keywords = {
            'time': ['time', 'busy', 'schedule', 'work'],
            'motivation': ['motivation', 'lazy', 'unmotivated', 'discipline'],
            'knowledge': ['know', 'confused', 'information', 'guidance'],
            'support': ['alone', 'support', 'help', 'accountability'],
            'money': ['money', 'expensive', 'budget', 'cost'],
            'stress': ['stress', 'anxiety', 'pressure', 'overwhelmed']
        }
        
        for obstacle, keywords in obstacle_keywords.items():
            if any(keyword in obstacles for keyword in keywords):
                profile["current_obstacles"].append(obstacle)
        
        # Obstacle severity
        if any(word in obstacles for word in ['impossible', 'can\'t', 'never', 'always']):
            profile["obstacle_severity"] = "high"
        elif any(word in obstacles for word in ['difficult', 'hard', 'challenging', 'struggle']):
            profile["obstacle_severity"] = "medium"
        else:
            profile["obstacle_severity"] = "low"
    
    def _extract_current_state(self, profile: Dict, responses: Dict):
        """Extract current activity and diet information"""
        current_activity = responses.get("current_activity", "").lower()
        current_diet = responses.get("current_diet", "").lower()
        
        # Activity level
        if any(word in current_activity for word in ['sedentary', 'desk', 'sitting', 'couch']):
            profile["current_activity_level"] = "sedentary"
        elif any(word in current_activity for word in ['walk', 'light', 'occasional', 'sometimes']):
            profile["current_activity_level"] = "light"
        elif any(word in current_activity for word in ['moderate', 'regular', 'few times']):
            profile["current_activity_level"] = "moderate"
        elif any(word in current_activity for word in ['active', 'gym', 'workout', 'exercise']):
            profile["current_activity_level"] = "active"
        elif any(word in current_activity for word in ['very active', 'daily', 'intense', 'athlete']):
            profile["current_activity_level"] = "very_active"
        
        # Diet quality assessment
        healthy_foods = ['vegetables', 'fruits', 'lean', 'protein', 'whole', 'organic', 'fresh']
        unhealthy_foods = ['fast food', 'junk', 'processed', 'sugar', 'soda', 'candy', 'fried']
        
        healthy_count = sum(1 for food in healthy_foods if food in current_diet)
        unhealthy_count = sum(1 for food in unhealthy_foods if food in current_diet)
        
        if healthy_count > unhealthy_count and healthy_count >= 3:
            profile["current_diet_quality"] = "excellent"
        elif healthy_count > unhealthy_count:
            profile["current_diet_quality"] = "good"
        elif healthy_count == unhealthy_count:
            profile["current_diet_quality"] = "fair"
        else:
            profile["current_diet_quality"] = "poor"
        
        profile["current_diet_details"] = current_diet
    
    def _extract_psychological_profile(self, profile: Dict, responses: Dict):
        """Extract psychological and behavioral patterns"""
        # This would be enhanced with more sophisticated NLP
        # For now, using simple keyword matching
        
        motivation_text = responses.get("initial_motivation", "").lower()
        obstacles_text = responses.get("main_obstacles", "").lower()
        
        # Confidence level
        if any(word in motivation_text for word in ['confident', 'ready', 'determined', 'sure']):
            profile["confidence_level"] = "high"
        elif any(word in motivation_text for word in ['maybe', 'try', 'hope', 'think']):
            profile["confidence_level"] = "medium"
        else:
            profile["confidence_level"] = "low"
        
        # Urgency level
        if any(word in motivation_text for word in ['urgent', 'now', 'immediately', 'asap']):
            profile["urgency_level"] = "high"
        elif any(word in motivation_text for word in ['soon', 'eventually', 'sometime']):
            profile["urgency_level"] = "medium"
        else:
            profile["urgency_level"] = "low"
    
    def _extract_dietary_preferences(self, profile: Dict, responses: Dict):
        """Extract dietary preferences and restrictions"""
        current_diet = responses.get("current_diet", "").lower()
        
        # Dietary restrictions
        restriction_keywords = {
            'vegetarian': ['vegetarian', 'no meat', 'plant-based'],
            'vegan': ['vegan', 'no animal', 'plant only'],
            'gluten_free': ['gluten-free', 'no gluten', 'celiac'],
            'dairy_free': ['dairy-free', 'no dairy', 'lactose'],
            'keto': ['keto', 'ketogenic', 'low carb'],
            'paleo': ['paleo', 'paleolithic'],
            'mediterranean': ['mediterranean', 'med diet']
        }
        
        for restriction, keywords in restriction_keywords.items():
            if any(keyword in current_diet for keyword in keywords):
                profile["dietary_restrictions"].append(restriction)
    
    def _extract_lifestyle_factors(self, profile: Dict, responses: Dict):
        """Extract lifestyle and practical factors"""
        # These would be enhanced with more specific questions
        # For now, inferring from available data
        
        obstacles = responses.get("main_obstacles", "").lower()
        
        if 'time' in obstacles or 'busy' in obstacles:
            profile["time_availability"] = "low"
        else:
            profile["time_availability"] = "medium"  # Default assumption
    
    def _extract_health_considerations(self, profile: Dict, responses: Dict):
        """Extract health-related information"""
        # This would be enhanced with specific health questions
        # For now, basic extraction from current state
        pass
    
    def _extract_behavioral_patterns(self, profile: Dict, responses: Dict):
        """Extract eating and behavioral patterns"""
        current_diet = responses.get("current_diet", "").lower()
        
        # Stress eating
        if any(word in current_diet for word in ['stress', 'anxiety', 'emotional', 'comfort']):
            profile["stress_eating"] = "yes"
        else:
            profile["stress_eating"] = "no"
    
    def _extract_success_factors(self, profile: Dict, responses: Dict):
        """Extract factors that contribute to success"""
        # This would be enhanced with specific questions about past successes
        pass
    
    def _calculate_derived_metrics(self, profile: Dict):
        """Calculate derived metrics like BMI, etc."""
        if profile["height_cm"] and profile["weight_kg"]:
            height_m = profile["height_cm"] / 100
            profile["bmi"] = round(profile["weight_kg"] / (height_m ** 2), 1)
    
    def generate_profile_summary(self, profile: Dict) -> str:
        """Generate a human-readable profile summary"""
        summary = f"""
USER PROFILE SUMMARY
===================

BASIC INFO:
- Discovery: {profile['discovery_method']}
- Motivation: {profile['motivation_strength']} ({profile['motivation_type']})
- Current Energy: {profile['current_energy_level']}
- Activity Level: {profile['current_activity_level']}
- Diet Quality: {profile['current_diet_quality']}

GOALS:
- Primary: {', '.join(profile['primary_goals']) if profile['primary_goals'] else 'Not specified'}
- Obstacles: {', '.join(profile['current_obstacles']) if profile['current_obstacles'] else 'None identified'}

PHYSICAL:
- Height: {profile['height_cm']}cm
- Weight: {profile['weight_kg']}kg
- BMI: {profile['bmi']}

DIETARY:
- Restrictions: {', '.join(profile['dietary_restrictions']) if profile['dietary_restrictions'] else 'None'}
- Stress Eating: {profile['stress_eating']}

PSYCHOLOGICAL:
- Confidence: {profile['confidence_level']}
- Urgency: {profile['urgency_level']}
- Time Available: {profile['time_availability']}
        """
        return summary.strip()
    
    def get_diet_recommendations(self, profile: Dict) -> List[str]:
        """Generate diet recommendations based on profile"""
        recommendations = []
        
        # Energy-based recommendations
        if profile["current_energy_level"] == "low":
            recommendations.append("Focus on iron-rich foods and complex carbohydrates for sustained energy")
        
        # Goal-based recommendations
        if "weight_loss" in profile["primary_goals"]:
            recommendations.append("Create a moderate calorie deficit with nutrient-dense foods")
        
        if "muscle_gain" in profile["primary_goals"]:
            recommendations.append("Increase protein intake to 1.6-2.2g per kg body weight")
        
        # Activity-based recommendations
        if profile["current_activity_level"] in ["active", "very_active"]:
            recommendations.append("Increase carbohydrate intake around workouts for performance")
        
        # Diet quality recommendations
        if profile["current_diet_quality"] in ["poor", "fair"]:
            recommendations.append("Focus on whole, unprocessed foods and reduce processed foods")
        
        return recommendations


