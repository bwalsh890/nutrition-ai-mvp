# 🚀 GitHub Setup Guide for Nutrition AI MVP

## Prerequisites

1. **Install Git for Windows**
   - Download from: https://git-scm.com/download/win
   - Run installer with default settings
   - **Important:** Select "Git from the command line and also from 3rd-party software"
   - Restart your terminal/PowerShell after installation

2. **Create GitHub Account** (if you don't have one)
   - Go to: https://github.com
   - Sign up for a free account
   - Verify your email address

## Step-by-Step Setup

### 1. Install Git
```bash
# Download and install Git from https://git-scm.com/download/win
# After installation, restart your terminal
```

### 2. Verify Git Installation
```bash
git --version
# Should show something like: git version 2.40.1.windows.1
```

### 3. Configure Git (First time only)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 4. Initialize Git Repository
```bash
# Navigate to your project directory
cd C:\Users\bwals\nutrition-ai-mvp

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Nutrition AI MVP with user onboarding and health profiles"
```

### 5. Create GitHub Repository
1. Go to https://github.com
2. Click "New repository" (green button)
3. Repository name: `nutrition-ai-mvp`
4. Description: `AI-powered nutrition application with personalized health recommendations`
5. Make it **Public** (so Claude can access it)
6. **Don't** initialize with README (we already have one)
7. Click "Create repository"

### 6. Connect Local Repository to GitHub
```bash
# Add GitHub remote (replace 'yourusername' with your GitHub username)
git remote add origin https://github.com/yourusername/nutrition-ai-mvp.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 7. Verify Setup
- Go to your GitHub repository
- You should see all your files
- The README.md should display with proper formatting

## 🎯 **Connecting Claude to Your Repository**

### Option 1: GitHub Integration (Recommended)
1. Go to [Claude.ai](https://claude.ai)
2. Look for GitHub integration options
3. Grant access to your `nutrition-ai-mvp` repository
4. Claude can now read, analyze, and suggest changes to your code

### Option 2: Share Repository URL
- Share your GitHub repository URL with Claude
- Example: `https://github.com/yourusername/nutrition-ai-mvp`

## 📁 **Current Project Structure**
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
├── README.md           # Project documentation
├── setup_git.bat       # Windows setup script
└── GITHUB_SETUP.md     # This guide
```

## 🔄 **Daily Workflow**

### Making Changes
```bash
# 1. Make your code changes
# 2. Stage changes
git add .

# 3. Commit changes
git commit -m "Description of changes"

# 4. Push to GitHub
git push origin main
```

### Pulling Changes (if working on multiple devices)
```bash
git pull origin main
```

## 🆘 **Troubleshooting**

### Git not recognized
- Restart your terminal after installing Git
- Make sure Git is added to your PATH

### Authentication issues
- Use GitHub CLI: `gh auth login`
- Or use personal access token instead of password

### Repository already exists
- Delete the existing repository on GitHub
- Or use a different name

## ✅ **Success Checklist**

- [ ] Git installed and working (`git --version`)
- [ ] GitHub account created
- [ ] Local repository initialized
- [ ] Files committed locally
- [ ] GitHub repository created
- [ ] Local repo connected to GitHub
- [ ] Code pushed to GitHub
- [ ] Claude can access the repository

## 🎉 **Next Steps**

Once everything is set up:
1. Share your repository URL with Claude
2. Ask Claude to analyze your code
3. Get suggestions for improvements
4. Collaborate on new features
5. Track issues and feature requests

---

**Your Nutrition AI MVP is ready for collaborative development! 🚀**
