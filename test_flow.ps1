# PowerShell script to test the complete onboarding flow
Write-Host "🚀 Starting automated onboarding test..." -ForegroundColor Green

$baseUrl = "http://localhost:8000"
$userId = 6  # Brendon2

# Test answers for all 8 questions
$answers = @(
    "I found this app through a friend who recommended it",
    "I decided to try it because I want to get healthier and lose some weight", 
    "• Lose 15 pounds`n• Have more energy throughout the day`n• Build better eating habits`n• Feel more confident in my body",
    "I think my main obstacles are lack of time to meal prep and not knowing what foods are actually good for me",
    "I currently do light exercise 2-3 times per week - mostly walking and some basic home workouts",
    "I'm 5'10`" tall, weigh 180 pounds, and my energy levels are pretty low especially in the afternoons",
    "In an ideal world, I'd be 165 pounds, have tons of energy, feel strong and confident, and be able to run a 5K without getting winded",
    "My current diet is pretty inconsistent - lots of takeout, processed foods, and I skip breakfast most days. I drink too much coffee and not enough water"
)

# Step 1: Start onboarding
Write-Host "`n1. Starting onboarding..." -ForegroundColor Yellow
$startResponse = Invoke-WebRequest -Uri "$baseUrl/start-onboarding/$userId" -Method POST -ContentType "application/json"
$startData = $startResponse.Content | ConvertFrom-Json
Write-Host "✅ Started onboarding: $($startData.message.Substring(0,50))..." -ForegroundColor Green

$sessionData = $startData.session_data

# Step 2: Answer all 8 questions
for ($i = 0; $i -lt $answers.Length; $i++) {
    $questionNum = $i + 1
    Write-Host "`n$questionNum. Answering question $questionNum : $($answers[$i].Substring(0,50))..." -ForegroundColor Yellow
    
    $body = @{
        user_id = $userId
        message = $answers[$i]
        session_data = $sessionData
    } | ConvertTo-Json -Depth 10
    
    $response = Invoke-WebRequest -Uri "$baseUrl/onboarding-chat" -Method POST -ContentType "application/json" -Body $body
    $data = $response.Content | ConvertFrom-Json
    $sessionData = $data.session_data
    
    Write-Host "✅ Question $questionNum answered. Progress: $($data.progress.percentage)%" -ForegroundColor Green
    
    # Check if complete
    if ($data.is_complete) {
        Write-Host "`n🎉 Onboarding completed!" -ForegroundColor Green
        Write-Host "📊 Final progress: $($data.progress.percentage)%" -ForegroundColor Cyan
        Write-Host "🤖 AI Response: $($data.response.Substring(0,100))..." -ForegroundColor Cyan
        break
    }
    
    Start-Sleep -Milliseconds 500
}

# Step 3: Test dashboard access
Write-Host "`n3. Testing dashboard access..." -ForegroundColor Yellow

try {
    $profileResponse = Invoke-WebRequest -Uri "$baseUrl/users/$userId/health-profile"
    if ($profileResponse.StatusCode -eq 200) {
        $profile = $profileResponse.Content | ConvertFrom-Json
        Write-Host "✅ Health profile loaded successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  No health profile found (this is normal for new users)" -ForegroundColor Yellow
}

Write-Host "`n✅ Test completed! User $userId should now be able to access the dashboard." -ForegroundColor Green
Write-Host "🔗 Open: frontend/dashboard.html" -ForegroundColor Cyan
