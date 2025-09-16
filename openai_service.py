import os
import asyncio
import logging
from openai import AsyncOpenAI
from config import settings
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

# Super Prompt - Complete AI-driven profiling
SYSTEM_MSG = """You are a health, nutrition, and psychology expert coach inside a diet optimization app. Your role is to guide the user through a friendly, conversational intake process to build their personal health profile.

Core Principles:
- Always speak warmly, simply, and conversationally — like a supportive coach
- Ask one question at a time. Wait for the user's answer before moving on
- Use gentle psychological techniques: mirror their language, show empathy, ask follow-up questions to uncover deeper motivations
- Dig into the "why" behind their goals (ask at least 2 follow-ups until the real motivation is clear)
- Encourage honesty and openness. Reassure them that all answers are useful, there are no "wrong" answers
- Keep foods and lifestyle recommendations practical, accessible, and non-weird (supermarket-available)

Data Points to Collect (minimum 10–12):
- Origin story — How did they arrive at the app? (Instagram, referral, curiosity, etc.)
- Motivation — Why now? Dig into deeper reasons (e.g., wedding, energy, confidence, health scare)
- Height (cm or ft/in)
- Current weight (kg or lbs)
- Goal weight (kg/lbs) or body composition goal
- Time frame to reach goal
- Daily activity level (desk job, walking, gym, sports, etc.)
- Exercise habits (frequency, type, intensity)
- Food preferences (animal-based, plant-based, vegetarian, whole-food, etc.)
- Foods they like (comfort foods, proteins, carbs, veggies they enjoy)
- Foods they dislike / won't eat (allergies, intolerances, dislikes, religious/cultural exclusions)
- Typical eating habits (meals/day, snacks, alcohol use, dining out, cooking style)
- Sleep & stress profile (hours slept, rested or tired, stress levels)
- Medical context (conditions, medications, intolerances)
- Support & accountability system (live with family/partner, prefer reminders/check-ins, prefer independence)
- Budget & cooking setup (time, money, preferred methods: BBQ, oven, pan, batch cooking, ordering out)

Flow:
1. Welcome & Rapport: Start with warmth: "Welcome — glad you're here." Ask origin: "What brought you to try this app today?"
2. Motivation (the deep why): Ask why they want to change now. Follow up twice to dig deeper: "And why is that important to you?" / "What do you hope will change if you achieve this?"
3. Health Metrics: Height, current weight, goal weight, timeframe
4. Lifestyle: Daily activity + exercise habits. Sleep & stress
5. Food Preferences: (animal, plant, mixed). Likes (favorite proteins, carbs, veggies). Dislikes (foods they won't eat). Eating habits (meals, snacks, alcohol). Cooking style & budget
6. Medical: Any allergies, intolerances, conditions, medications
7. Accountability Style: Do they want reminders, check-ins, or more freedom?
8. Confirmation: Recap their answers back to them. Ask if anything important is missing

Important Rules:
- Do not suggest cheat foods or treats at this stage
- Do not build the diet plan yet — only gather the health profile
- Always give the user a chance to push back ("I don't eat that," "That doesn't work for me")
- After completing the profile, clearly summarize all data points in an easy-to-read list
- End by saying: "Thanks — I've got your full health profile now. From here, I'll create a personalized, nutrient-dense diet plan that helps you reach your goals while still being practical and enjoyable. Would you like me to build that plan now?"

This ensures every user ends up with a complete profile (motivation + metrics + lifestyle + food context), while keeping the process natural and trust-building."""

# Developer prompt for tool control
DEV_MSG = """You are now in tool-calling mode. Your job is to:

1. Have natural conversations to collect all required profile data
2. When you have enough information for a field, mentally note it
3. When ALL required fields are collected, call save_profile with the complete data
4. After saving the profile, call generate_meal_plan to create their personalized plan

Required fields for save_profile:
- goal (fat_loss/maintenance/muscle_gain)
- target_calories (1200-5000)
- activity_pattern (desk/standing/outdoor)
- exercise_summary (string)
- exercise_intensity (none_low/mixed/high)
- protein_preferences (array of strings)
- organ_meats (boolean)
- seafood_frequency (none/weekly/2-3x_wk/daily)
- carb_choices (array: sweet_potato/white_potato/rice/quinoa)
- fat_choices (array: avocado/olive_oil/nuts_seeds/animal_fats)
- veg_likes (array of strings)
- colors_ok (boolean)
- sulfur_ok (boolean)
- diet_style (animal_focused/plant_focused/whole_food_mix/vegetarian/vegan)
- ferments_ok (boolean)
- meals_pattern (string description)
- constraints (array of strings - allergies/intolerances)
- dislikes (array of strings)
- region (default: AU)
- kcal_confidence (0-1)

Only call tools when you have complete, confident data. Continue the conversation naturally until then."""

# Profile schema for structured data collection
PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "goal": {"type": "string", "enum": ["fat_loss", "maintenance", "muscle_gain"]},
        "target_calories": {"type": "integer", "minimum": 1200, "maximum": 5000},
        "activity_pattern": {"type": "string", "description": "desk/standing/outdoor"},
        "exercise_summary": {"type": "string"},
        "exercise_intensity": {"type": "string", "enum": ["none_low", "mixed", "high"]},
        "protein_preferences": {"type": "array", "items": {"type": "string"}},
        "organ_meats": {"type": "boolean"},
        "seafood_frequency": {"type": "string", "enum": ["none", "weekly", "2-3x_wk", "daily"]},
        "carb_choices": {"type": "array", "items": {"type": "string", "enum": ["sweet_potato", "white_potato", "rice", "quinoa"]}},
        "fat_choices": {"type": "array", "items": {"type": "string", "enum": ["avocado", "olive_oil", "nuts_seeds", "animal_fats"]}},
        "veg_likes": {"type": "array", "items": {"type": "string"}},
        "colors_ok": {"type": "boolean"},
        "sulfur_ok": {"type": "boolean"},
        "diet_style": {"type": "string", "enum": ["animal_focused", "plant_focused", "whole_food_mix", "vegetarian", "vegan"]},
        "ferments_ok": {"type": "boolean"},
        "meals_pattern": {"type": "string", "description": "e.g., small breakfast, big lunch, snack, dinner"},
        "constraints": {"type": "array", "items": {"type": "string"}, "description": "allergies/intolerances"},
        "dislikes": {"type": "array", "items": {"type": "string"}},
        "region": {"type": "string", "default": "AU"},
        "kcal_confidence": {"type": "number", "minimum": 0, "maximum": 1}
    },
    "required": ["goal", "exercise_intensity", "diet_style"]
}

# Tool definitions for function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "save_profile",
            "description": "Persist user profile when enough data is collected",
            "parameters": PROFILE_SCHEMA
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_meal_plan",
            "description": "Create personalized meal plan from profile",
            "parameters": {
                "type": "object",
                "properties": {"profile_id": {"type": "string"}},
                "required": ["profile_id"]
            }
        }
    }
]

class OpenAIService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key or self.api_key == "REPLACE_WITH_YOUR_ACTUAL_OPENAI_API_KEY":
            logger.warning("OpenAI API key not configured - using fallback responses")
            self.client = None
        else:
            try:
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"OpenAI client initialization failed: {e} - using fallback responses")
                self.client = None

    async def respond(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None, response_format: Optional[Dict] = None, stream: bool = False) -> Any:
        """Main method for OpenAI API calls with tool calling support"""
        if not self.client:
            return self._get_fallback_response()
        
        try:
            params = {
                "model": "gpt-4o-mini",  # Using latest model
                "messages": messages,
                "temperature": 0.7,
            }
            
            if tools:
                params["tools"] = tools
            if response_format:
                params["response_format"] = response_format
            if stream:
                params["stream"] = True

            if stream:
                # Handle streaming responses
                stream = await self.client.chat.completions.create(**params)
                chunks = []
                async for event in stream:
                    if event.choices:
                        delta = event.choices[0].delta.get("content", "")
                        if delta:
                            chunks.append(delta)
                return "".join(chunks)
            else:
                response = await self.client.chat.completions.create(**params)
                return response
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_fallback_response()

    async def chat_completion(self, message: str, conversation_history: List = None, health_profile: dict = None) -> str:
        """Legacy method for backward compatibility"""
        if not self.client:
            return "I'm currently in demo mode. Please configure your OpenAI API key to enable AI responses."
        
        try:
            messages = []
            
            # Add system message
            system_message = "You are a helpful nutrition and health AI assistant. Provide personalized advice based on the user's health profile and conversation history."
            if health_profile:
                system_message += f"\n\nUser's health profile: {health_profile}"
            
            messages.append({"role": "system", "content": system_message})
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    messages.append({"role": msg.role, "content": msg.content})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Make API call
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again."

    def _get_fallback_response(self) -> str:
        """Fallback response when API is not available"""
        return "I'm currently in demo mode. Please configure your OpenAI API key to enable AI responses."

# Create a singleton instance
openai_service = None

def get_openai_service() -> OpenAIService:
    global openai_service
    if openai_service is None:
        openai_service = OpenAIService()
    return openai_service