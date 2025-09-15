import React, { useState, useEffect, useRef } from 'react';

interface Message {
  id: string;
  type: 'ai' | 'user';
  content: string;
  timestamp: Date;
}

interface UserProfile {
  // Deep Discovery (12 points)
  mainMotivation: string;
  currentEnergyLevel: number;
  desiredEnergyLevel: number;
  coreValues: string[];
  foodRelationship: string;
  pastSuccesses: string[];
  mainObstacles: string[];
  sixMonthVision: string;
  identityGoal: string;
  supportSystem: string;
  deepWhy: string;
  commitmentLevel: number;
  
  // Nutritional Requirements (8 points)
  height: number;
  currentWeight: number;
  targetWeight: number;
  timeframe: string;
  exerciseFrequency: number;
  exerciseIntensity: string;
  noGoFoods: string[];
  dietaryStyle: string;
}

const CORE_QUESTIONS = [
  {
    id: 1,
    question: "What brought you here today? What's really going on with your health and energy?",
    followUp: "On a scale of 1-10, how motivated do you feel to make changes? 1 being it feels overwhelming, 10 being you're ready to tackle anything.",
    dataPoint: 'mainMotivation'
  },
  {
    id: 2,
    question: "Tell me about a typical day - how do you feel in your body from morning to night?",
    followUp: "On a scale of 1-10, where would you put your current energy level? 1 being completely drained, 10 being full of energy.",
    dataPoint: 'currentEnergyLevel'
  },
  {
    id: 3,
    question: "When you imagine having the energy you truly want, what would that give you? What becomes possible?",
    followUp: "On a scale of 1-10, how would you rate your desired energy level? 1 being just getting by, 10 being unstoppable.",
    dataPoint: 'desiredEnergyLevel'
  },
  {
    id: 4,
    question: "What matters most to you in life right now? Who depends on you being at your best?",
    followUp: "On a scale of 1-10, how important is this to you? 1 being nice to have, 10 being absolutely critical.",
    dataPoint: 'coreValues'
  },
  {
    id: 5,
    question: "How do you feel about food and eating? What emotions come up?",
    followUp: "On a scale of 1-10, how would you rate your relationship with food right now? 1 being it feels like a constant battle, 10 being you feel in control.",
    dataPoint: 'foodRelationship'
  },
  {
    id: 6,
    question: "What's worked for you before, even briefly? What made you feel amazing?",
    followUp: "On a scale of 1-10, how confident do you feel about making changes? 1 being not at all, 10 being very confident.",
    dataPoint: 'pastSuccesses'
  },
  {
    id: 7,
    question: "What gets in your way? When do you struggle most with healthy choices?",
    followUp: "On a scale of 1-10, how challenging do these obstacles feel? 1 being easy to overcome, 10 being almost impossible.",
    dataPoint: 'mainObstacles'
  },
  {
    id: 8,
    question: "Six months from now, if everything went perfectly, how would you feel? What would be different?",
    followUp: "On a scale of 1-10, how excited are you about this vision? 1 being not really, 10 being incredibly excited.",
    dataPoint: 'sixMonthVision'
  },
  {
    id: 9,
    question: "Who are you becoming through this journey? What kind of person do you want to be?",
    followUp: "On a scale of 1-10, how aligned do you feel with this identity? 1 being not at all, 10 being completely aligned.",
    dataPoint: 'identityGoal'
  },
  {
    id: 10,
    question: "Who celebrates your wins? Who would notice if you transformed your health?",
    followUp: "On a scale of 1-10, how supported do you feel? 1 being completely alone, 10 being very supported.",
    dataPoint: 'supportSystem'
  },
  {
    id: 11,
    question: "Why does this matter to you at the deepest level? What's at stake if nothing changes?",
    followUp: "On a scale of 1-10, how urgent does this feel? 1 being not urgent, 10 being extremely urgent.",
    dataPoint: 'deepWhy'
  },
  {
    id: 12,
    question: "What makes this time different? What's your one word for this journey?",
    followUp: "On a scale of 1-10, how committed are you? 1 being just exploring, 10 being all in.",
    dataPoint: 'commitmentLevel'
  }
];

const NUTRITIONAL_QUESTIONS = [
  {
    id: 13,
    question: "To understand your energy needs better, what's your current height in centimeters?",
    dataPoint: 'height'
  },
  {
    id: 14,
    question: "And what's your current weight in kilograms?",
    dataPoint: 'currentWeight'
  },
  {
    id: 15,
    question: "What weight would help you feel the way you want to feel?",
    dataPoint: 'targetWeight'
  },
  {
    id: 16,
    question: "By when would you like to reach this goal?",
    dataPoint: 'timeframe'
  },
  {
    id: 17,
    question: "How many times per week do you exercise?",
    dataPoint: 'exerciseFrequency'
  },
  {
    id: 18,
    question: "What intensity would you say your workouts are - low, medium, or high?",
    dataPoint: 'exerciseIntensity'
  },
  {
    id: 19,
    question: "Are there any foods you absolutely can't eat or don't want to eat?",
    dataPoint: 'noGoFoods'
  },
  {
    id: 20,
    question: "What kind of eating style appeals to you - omnivore, vegetarian, keto, paleo, or something else?",
    dataPoint: 'dietaryStyle'
  }
];

const OnboardingChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [userProfile, setUserProfile] = useState<Partial<UserProfile>>({});
  const [isWaitingForScore, setIsWaitingForScore] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Start the conversation
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: '1',
        type: 'ai',
        content: "Hi! I'm here to help you discover your personalized nutrition path. This conversation will help me understand what matters most to you and build a plan that truly fits your life. Let's start with what brought you here today.",
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, []);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    // Process the response
    setTimeout(() => {
      processUserResponse(inputValue);
    }, 1000);
  };

  const processUserResponse = (response: string) => {
    const allQuestions = [...CORE_QUESTIONS, ...NUTRITIONAL_QUESTIONS];
    const currentQ = allQuestions[currentQuestion];

    if (isWaitingForScore) {
      // Extract score from response
      const score = extractScore(response);
      if (score !== null) {
        updateUserProfile(currentQ.dataPoint, score);
        setIsWaitingForScore(false);
        moveToNextQuestion();
      } else {
        askForScoreAgain();
      }
    } else {
      // Store qualitative response
      updateUserProfile(currentQ.dataPoint, response);
      
      // Ask for score if it's a core question
      if (currentQuestion < CORE_QUESTIONS.length && currentQ.followUp) {
        askForScore(currentQ.followUp);
      } else {
        moveToNextQuestion();
      }
    }
  };

  const extractScore = (response: string): number | null => {
    const match = response.match(/(\d+)/);
    return match ? parseInt(match[1]) : null;
  };

  const updateUserProfile = (dataPoint: string, value: any) => {
    setUserProfile(prev => ({
      ...prev,
      [dataPoint]: value
    }));
  };

  const askForScore = (followUp: string) => {
    const aiMessage: Message = {
      id: Date.now().toString(),
      type: 'ai',
      content: followUp,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, aiMessage]);
    setIsWaitingForScore(true);
  };

  const askForScoreAgain = () => {
    const aiMessage: Message = {
      id: Date.now().toString(),
      type: 'ai',
      content: "I need a number from 1-10 to help me understand better. Could you give me a score?",
      timestamp: new Date()
    };
    setMessages(prev => [...prev, aiMessage]);
  };

  const moveToNextQuestion = () => {
    const allQuestions = [...CORE_QUESTIONS, ...NUTRITIONAL_QUESTIONS];
    
    if (currentQuestion < allQuestions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
      const nextQ = allQuestions[currentQuestion + 1];
      
      const aiMessage: Message = {
        id: Date.now().toString(),
        type: 'ai',
        content: nextQ.question,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
    } else {
      // Conversation complete
      completeOnboarding();
    }
  };

  const completeOnboarding = () => {
    const completionMessage: Message = {
      id: Date.now().toString(),
      type: 'ai',
      content: "Perfect! I now have everything I need to build your personalized nutrition plan. Let me create your mission statement and then we'll move to your dashboard.",
      timestamp: new Date()
    };
    setMessages(prev => [...prev, completionMessage]);
    setIsComplete(true);
  };

  const generateMissionStatement = () => {
    const { mainMotivation, deepWhy, sixMonthVision } = userProfile;
    return `I want ${mainMotivation} so I can ${sixMonthVision} because ${deepWhy}`;
  };

  if (isComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl w-full">
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Personal Mission</h2>
            <div className="bg-gray-50 rounded-lg p-6 mb-6">
              <p className="text-lg text-gray-700 italic">"{generateMissionStatement()}"</p>
            </div>
            <p className="text-gray-600 mb-8">I've built your personalized nutrition plan based on everything you've shared. Ready to start your journey?</p>
            <button 
              onClick={() => window.location.href = '/'}
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Start Your Journey
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow-sm border-b p-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl font-semibold text-gray-900">Discover Your Nutrition Path</h1>
          <div className="mt-2">
            <div className="bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentQuestion + 1) / (CORE_QUESTIONS.length + NUTRITIONAL_QUESTIONS.length)) * 100}%` }}
              />
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Question {currentQuestion + 1} of {CORE_QUESTIONS.length + NUTRITIONAL_QUESTIONS.length}
            </p>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-900 shadow-sm'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p className="text-xs opacity-70 mt-1">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex space-x-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type your response..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isComplete}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isComplete}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingChat;
