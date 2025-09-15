# 🥗 Nutrition AI MVP

A comprehensive FastAPI-based nutrition AI application with personalized health recommendations, user management, and intelligent meal planning.

## ✨ Features

### 🔐 User Management
- User registration and authentication
- Secure password hashing with bcrypt
- User profile management

### 🏥 Health Profile System
- Comprehensive health data collection
- Age, gender, height, weight tracking
- Activity level monitoring
- Dietary restrictions and allergies
- Health conditions and medications
- Fitness goals tracking

### 🤖 AI-Powered Nutrition Advice
- Personalized recommendations based on health profile
- Context-aware meal suggestions
- Dietary restriction compliance
- Health condition considerations
- Medication interactions awareness

### 📊 Usage Management
- Message limiting (50 per month per user)
- Usage tracking and monitoring
- Monthly reset functionality

### 🛡️ Security & Performance
- CORS middleware for cross-origin requests
- Input validation with Pydantic
- SQLAlchemy ORM for database operations
- Error handling and logging

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Git (for version control)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/nutrition-ai-mvp.git
cd nutrition-ai-mvp
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables:**
```bash
# Windows PowerShell
$env:DATABASE_URL="sqlite:///./nutrition_ai.db"
$env:SECRET_KEY="your-secret-key-change-this-in-production"
$env:OPENAI_API_KEY="your-openai-api-key-here"

# Linux/Mac
export DATABASE_URL="sqlite:///./nutrition_ai.db"
export SECRET_KEY="your-secret-key-change-this-in-production"
export OPENAI_API_KEY="your-openai-api-key-here"
```

4. **Run the application:**
```bash
python main.py
```

5. **Access the API:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 📚 API Documentation

### Core Endpoints

#### User Management
- `POST /users/` - Create new user
- `GET /users/` - List all users
- `GET /users/{user_id}` - Get specific user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

#### Health Profiles
- `POST /users/{user_id}/health-profile` - Create health profile
- `GET /users/{user_id}/health-profile` - Get health profile
- `PUT /users/{user_id}/health-profile` - Update health profile
- `DELETE /users/{user_id}/health-profile` - Delete health profile

#### AI Chat
- `POST /chat` - Chat with nutrition AI
- `GET /users/{user_id}/message-usage` - Check message usage

### Example Usage

#### 1. Create a User
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

#### 2. Create Health Profile
```bash
curl -X POST "http://localhost:8000/users/1/health-profile" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 30,
    "gender": "female",
    "height_cm": 165,
    "weight_kg": 60,
    "activity_level": "moderately_active",
    "dietary_restrictions": ["vegetarian", "gluten-free"],
    "health_conditions": ["diabetes"],
    "fitness_goals": ["weight_loss", "muscle_gain"],
    "allergies": ["nuts", "shellfish"],
    "medications": ["metformin"]
  }'
```

#### 3. Chat with AI
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What should I eat for breakfast?",
    "user_id": 1,
    "conversation_history": []
  }'
```

## 🏗️ Architecture

### Database Schema
- **Users**: User accounts and authentication
- **UserHealthProfiles**: Comprehensive health data
- **MessageTracking**: Usage monitoring and limits

### Key Components
- **FastAPI**: Web framework and API endpoints
- **SQLAlchemy**: Database ORM and models
- **Pydantic**: Data validation and serialization
- **OpenAI API**: AI-powered nutrition advice
- **SQLite**: Local database for development

## 🔧 Development

### Project Structure
```
nutrition-ai-mvp/
├── main.py              # FastAPI application
├── models.py            # Database models
├── schemas.py           # Pydantic schemas
├── crud.py              # Database operations
├── database.py          # Database configuration
├── config.py            # Application settings
├── openai_service.py    # OpenAI integration
├── requirements.txt     # Dependencies
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

### Adding New Features
1. Create database models in `models.py`
2. Add Pydantic schemas in `schemas.py`
3. Implement CRUD operations in `crud.py`
4. Add API endpoints in `main.py`
5. Update tests and documentation

## 🚀 Deployment

### Production Considerations
- Use PostgreSQL instead of SQLite
- Set up proper environment variable management
- Configure CORS for your frontend domain
- Set up monitoring and logging
- Use a production ASGI server like Gunicorn

### Docker Support
```bash
# Build and run with Docker
docker-compose up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the code examples in this README

---

**Built with ❤️ using FastAPI, SQLAlchemy, and OpenAI**