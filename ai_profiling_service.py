import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai_service import get_openai_service, SYSTEM_MSG, DEV_MSG, TOOLS, PROFILE_SCHEMA

logger = logging.getLogger(__name__)

class AIProfilingService:
    def __init__(self):
        self.openai_service = get_openai_service()

    async def start_profiling(self, user_id: int) -> Dict[str, Any]:
        """Start the AI profiling conversation - completely GPT-driven"""
        session_data = {
            "user_id": user_id,
            "conversation_history": [],
            "collected_data": {},
            "started_at": datetime.now().isoformat(),
            "is_complete": False,
            "profile_data": None
        }
        
        # Let GPT handle the entire initial conversation
        initial_message = await self._get_initial_message()
        
        return {
            "message": initial_message,
            "session_data": session_data
        }

    async def process_user_response(self, session_data: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Process user response - completely GPT-driven with tool calling"""
        try:
            # Add user message to conversation history
            session_data["conversation_history"].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })

            # Check if profiling is already complete
            if session_data.get("is_complete", False):
                return {
                    "response": "Your profile is already complete! Would you like me to create your personalized meal plan?",
                    "session_data": session_data
                }

            # Let GPT handle the entire conversation and tool calling
            ai_response, tool_calls = await self._get_ai_response_with_tools(session_data["conversation_history"])

            # Add AI response to conversation history
            session_data["conversation_history"].append({
                "role": "assistant", 
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            })

            # Handle any tool calls from GPT
            if tool_calls:
                await self._handle_tool_calls(tool_calls, session_data)

            return {
                "response": ai_response,
                "session_data": session_data,
                "is_complete": session_data.get("is_complete", False)
            }

        except Exception as e:
            logger.error(f"Error processing user response: {e}")
            return {
                "response": "I'm sorry, I encountered an error. Could you please try again?",
                "session_data": session_data,
                "is_complete": False
            }

    async def _get_initial_message(self) -> str:
        """Get the initial AI message - let GPT decide how to start"""
        try:
            messages = [
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user", "content": "A new user has just opened the app. Start the conversation naturally to begin building their health profile."}
            ]
            
            response = await self.openai_service.respond(messages)
            
            if response and hasattr(response, 'choices'):
                return response.choices[0].message.content or "Welcome! I'm here to help you with your nutrition goals. What brought you here today?"
            else:
                return "Welcome! I'm here to help you with your nutrition goals. What brought you here today?"
                
        except Exception as e:
            logger.error(f"Error getting initial message: {e}")
            return "Welcome! I'm here to help you with your nutrition goals. What brought you here today?"

    async def _get_ai_response_with_tools(self, conversation_history: List[Dict]) -> tuple[str, List[Dict]]:
        """Get AI response with tool calling - let GPT decide when to call tools"""
        try:
            # Build messages with Super Prompt context
            messages = [
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user", "content": DEV_MSG}
            ]
            
            # Add conversation history
            for msg in conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Get AI response with tool calling enabled
            response = await self.openai_service.respond(messages, tools=TOOLS)
            
            if not response or not hasattr(response, 'choices'):
                return "I'm here to help you build your health profile. What brought you here today?", []
            
            choice = response.choices[0]
            
            # Check if AI wants to call tools
            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                return choice.message.content or "I'm processing your information...", choice.message.tool_calls
            else:
                return choice.message.content or "I'm here to help you. What would you like to share?", []
                
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return "I'm here to help you build your health profile. What brought you here today?", []

    async def _handle_tool_calls(self, tool_calls: List[Dict], session_data: Dict[str, Any]) -> None:
        """Handle tool calls from GPT - save profile or generate meal plan"""
        try:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "save_profile":
                    # GPT has collected enough data to save the profile
                    session_data["profile_data"] = function_args
                    session_data["collected_data"] = function_args
                    session_data["is_complete"] = True
                    session_data["completed_at"] = datetime.now().isoformat()
                    logger.info(f"Profile saved for user {session_data['user_id']}: {function_args}")
                    
                elif function_name == "generate_meal_plan":
                    # GPT wants to generate a meal plan
                    profile_id = function_args.get("profile_id")
                    logger.info(f"Meal plan generation requested for profile {profile_id}")
            
        except Exception as e:
            logger.error(f"Error handling tool calls: {e}")

    def build_meal_plan(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build a personalized meal plan from profile data"""
        # This would integrate with your existing meal plan generation logic
        return {
            "message": "Meal plan generation not yet implemented",
            "profile_data": profile_data
        }