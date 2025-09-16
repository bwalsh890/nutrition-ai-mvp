from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
from profile_builder import UserProfileBuilder

class OnboardingChatService:
    def __init__(self):
        self.profile_builder = UserProfileBuilder()
        self.questions = [
            {
                "id": 1,
                "question": "How did you find this app?",
                "data_points": ["discovery_method"],
                "type": "direct_text"
            },
            {
                "id": 2,
                "question": "Why did you decide to try it?",
                "data_points": ["initial_motivation"],
                "type": "direct_text"
            },
            {
                "id": 3,
                "question": "Can you give me 3-4 dot points of what you're hoping to change?",
                "data_points": ["hopes_goals"],
                "type": "direct_text"
            },
            {
                "id": 4,
                "question": "What do you think is holding you back from doing this now?",
                "data_points": ["main_obstacles"],
                "type": "direct_text"
            },
            {
                "id": 5,
                "question": "Can you tell me about your current activity level?",
                "data_points": ["current_activity"],
                "type": "direct_text"
            },
            {
                "id": 6,
                "question": "Can you give me your current height, weight and energy levels?",
                "data_points": ["basic_measurements"],
                "type": "direct_text"
            },
            {
                "id": 7,
                "question": "Can you describe to me in an ideal world how you would look, feel and even perform?",
                "data_points": ["ideal_vision"],
                "type": "direct_text"
            },
            {
                "id": 8,
                "question": "Can you describe to me in as much detail as possible your current diet.",
                "data_points": ["current_diet"],
                "type": "direct_text"
            }
        ]
    
    def get_next_question(self, session_data: Dict) -> Optional[Dict]:
        """Get the next question based on current session state"""
        current_question_id = session_data.get("current_question_id", 0)
        waiting_for_follow_up = session_data.get("waiting_for_follow_up", False)
        
        if current_question_id >= len(self.questions):
            return None  # All questions completed
        
        question = self.questions[current_question_id]
        
        if waiting_for_follow_up and question.get("follow_up"):
            return {
                "question": question["follow_up"],
                "type": "follow_up",
                "expecting": "score"
            }
        else:
            return {
                "question": question["question"],
                "type": question["type"],
                "choices": question.get("choices"),
                "question_id": question["id"]
            }
    
    def process_response(self, session_data: Dict, user_response: str) -> Tuple[Dict, str]:
        """Process user response and return updated session data and next message"""
        current_question_id = session_data.get("current_question_id", 0)
        waiting_for_follow_up = session_data.get("waiting_for_follow_up", False)
        collected_data = session_data.get("collected_data", {})
        
        if current_question_id >= len(self.questions):
            return session_data, "Thank you! I have all the information I need."
        
        question = self.questions[current_question_id]
        
        # Process the response based on question type
        if waiting_for_follow_up:
            # Check if this is a score-based follow-up or qualitative follow-up
            if question["type"] == "qualitative_then_score":
                # Extract score from follow-up response
                score = self._extract_score(user_response)
                if score is not None:
                    # Save the score
                    data_point = question["data_points"][1]  # Second data point is always the score
                    collected_data[data_point] = score
                    
                    # Move to next question
                    session_data.update({
                        "current_question_id": current_question_id + 1,
                        "waiting_for_follow_up": False,
                        "collected_data": collected_data
                    })
                    
                    # Get next question
                    next_q = self.get_next_question(session_data)
                    if next_q:
                        return session_data, next_q["question"]
                    else:
                        return session_data, "Perfect! I now have everything I need to create your personalized plan."
                else:
                    return session_data, "I need a number from 1-10. Could you give me a score?"
            else:
                # Qualitative follow-up - just save the response and move on
                data_point = question["data_points"][1]  # Second data point
                collected_data[data_point] = user_response
                
                # Move to next question
                session_data.update({
                    "current_question_id": current_question_id + 1,
                    "waiting_for_follow_up": False,
                    "collected_data": collected_data
                })
                
                # Get next question
                next_q = self.get_next_question(session_data)
                if next_q:
                    return session_data, next_q["question"]
                else:
                    return session_data, "Perfect! I now have everything I need to create your personalized plan."
        
        else:
            # Process main question response
            if question["type"] in ["qualitative_then_score", "qualitative_then_qualitative"]:
                # Save qualitative response
                data_point = question["data_points"][0]
                collected_data[data_point] = user_response
                
                # Set up for follow-up
                session_data.update({
                    "waiting_for_follow_up": True,
                    "collected_data": collected_data
                })
                
                follow_up = self.get_next_question(session_data)
                return session_data, follow_up["question"]
            
            elif question["type"] in ["direct_numeric", "direct_text", "direct_choice"]:
                # Validate and save direct response
                if self._validate_response(question, user_response):
                    data_point = question["data_points"][0]
                    collected_data[data_point] = user_response
                    
                    # Move to next question
                    session_data.update({
                        "current_question_id": current_question_id + 1,
                        "waiting_for_follow_up": False,
                        "collected_data": collected_data
                    })
                    
                    next_q = self.get_next_question(session_data)
                    if next_q:
                        return session_data, next_q["question"]
                    else:
                        return session_data, "Perfect! I now have everything I need to create your personalized plan."
                else:
                    return session_data, self._get_validation_message(question)
    
    def _extract_score(self, response: str) -> Optional[int]:
        """Extract a 1-10 score from user response"""
        import re
        numbers = re.findall(r'\b([1-9]|10)\b', response)
        if numbers:
            score = int(numbers[0])
            return score if 1 <= score <= 10 else None
        return None
    
    def _validate_response(self, question: Dict, response: str) -> bool:
        """Validate response based on question type"""
        try:
            if question["type"] == "direct_numeric":
                value = float(response)
                if "validation" in question:
                    return question["validation"](response)
                return True
            elif question["type"] == "direct_choice":
                return response.lower() in [choice.lower() for choice in question.get("choices", [])]
            else:
                return len(response.strip()) > 0
        except:
            return False
    
    def _get_validation_message(self, question: Dict) -> str:
        """Get validation error message for question"""
        if question["type"] == "direct_numeric":
            return "Please enter a valid number."
        elif question["type"] == "direct_choice":
            choices = ", ".join(question.get("choices", []))
            return f"Please choose from: {choices}"
        else:
            return "Please provide a response."
    
    def build_user_profile(self, collected_data: Dict) -> Dict:
        """Build comprehensive user profile from collected data"""
        return self.profile_builder.build_profile(collected_data)
    
    def get_profile_summary(self, collected_data: Dict) -> str:
        """Get human-readable profile summary"""
        profile = self.build_user_profile(collected_data)
        return self.profile_builder.generate_profile_summary(profile)
    
    def get_diet_recommendations(self, collected_data: Dict) -> List[str]:
        """Get diet recommendations based on profile"""
        profile = self.build_user_profile(collected_data)
        return self.profile_builder.get_diet_recommendations(profile)
