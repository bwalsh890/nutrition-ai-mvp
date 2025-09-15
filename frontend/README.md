# Nutrition AI - Habit Tracker Frontend

A mobile-optimized React frontend for the Nutrition AI habit tracking system.

## Features

- 📱 **Mobile-First Design** - Optimized for mobile devices with responsive layout
- 📊 **Questionnaire Flow** - Multi-step questionnaire to set up personalized habits
- 🎯 **Habit Tracking** - Daily habit logging with progress visualization
- 📈 **Progress Charts** - Interactive charts showing daily, weekly, and monthly progress
- 💡 **Smart Feedback** - Personalized feedback and encouragement based on performance
- 🎨 **Modern UI** - Clean, intuitive interface with Tailwind CSS

## Components

- **Questionnaire** - Multi-step form for initial setup
- **Dashboard** - Overview of today's progress and quick stats
- **HabitTracker** - Daily habit logging interface
- **Progress** - Charts and detailed progress tracking
- **Navigation** - Bottom navigation for mobile

## Tech Stack

- React 18 with TypeScript
- Tailwind CSS for styling
- Recharts for data visualization
- Axios for API communication
- React Router for navigation
- Lucide React for icons

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## API Integration

The frontend connects to the FastAPI backend running on `http://localhost:8000`. Make sure the backend is running before starting the frontend.

## Mobile Optimization

- Responsive design that works on all screen sizes
- Touch-friendly interface with appropriate button sizes
- Bottom navigation for easy thumb navigation
- Optimized for portrait orientation
- Fast loading with minimal bundle size

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm eject` - Ejects from Create React App (one-way operation)
