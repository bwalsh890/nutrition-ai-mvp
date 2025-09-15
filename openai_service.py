from openai import OpenAI
from config import settings
from schemas import ChatMessage
from typing import List
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-3.5-turbo"
    
    async def chat_completion(self, message: str, conversation_history: List[ChatMessage] = None, health_profile: dict = None) -> str:
        """
        Send a message to OpenAI and get a response
        """
        try:
            # Prepare messages for OpenAI
            messages = []
            
            # Build personalized system prompt based on health profile
            system_prompt = "You are a helpful nutrition AI assistant. You provide accurate, evidence-based nutrition advice and help users with their dietary questions and meal planning. Always be encouraging and supportive while providing practical, actionable advice."
            
            if health_profile:
                system_prompt += "\n\nIMPORTANT: Use the following user health information to provide personalized advice:\n"
                
                if health_profile.get('age'):
                    system_prompt += f"- Age: {health_profile['age']} years old\n"
                if health_profile.get('gender'):
                    system_prompt += f"- Gender: {health_profile['gender']}\n"
                if health_profile.get('height_cm') and health_profile.get('weight_kg'):
                    system_prompt += f"- Height: {health_profile['height_cm']}cm, Weight: {health_profile['weight_kg']}kg\n"
                if health_profile.get('activity_level'):
                    system_prompt += f"- Activity Level: {health_profile['activity_level']}\n"
                
                if health_profile.get('dietary_restrictions'):
                    system_prompt += f"- Dietary Restrictions: {', '.join(health_profile['dietary_restrictions'])}\n"
                if health_profile.get('health_conditions'):
                    system_prompt += f"- Health Conditions: {', '.join(health_profile['health_conditions'])}\n"
                if health_profile.get('fitness_goals'):
                    system_prompt += f"- Fitness Goals: {', '.join(health_profile['fitness_goals'])}\n"
                if health_profile.get('allergies'):
                    system_prompt += f"- Allergies: {', '.join(health_profile['allergies'])}\n"
                if health_profile.get('medications'):
                    system_prompt += f"- Medications: {', '.join(health_profile['medications'])}\n"
                
                system_prompt += "\nAlways consider these factors when providing nutrition advice and make recommendations that are safe and appropriate for this user's specific situation."
            
            messages.append({
                "role": "system",
                "content": system_prompt
            })
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later."

# Create a singleton instance
openai_service = None

def get_openai_service() -> OpenAIService:
    global openai_service
    if openai_service is None:
        openai_service = OpenAIService()
    return openai_service
