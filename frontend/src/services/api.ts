import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Questionnaire {
  id: number;
  user_id: number;
  sleep_hours?: number;
  water_goal_ml?: number;
  meal_frequency?: number;
  exercise_frequency?: number;
  exercise_duration?: number;
  stress_level?: string;
  energy_level?: string;
  mood_tracking: boolean;
  weight_goal?: string;
  target_weight_kg?: number;
  created_at: string;
  updated_at?: string;
}

export interface HabitTarget {
  id: number;
  user_id: number;
  habit_type: string;
  target_value: number;
  target_unit: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface HabitLog {
  id: number;
  user_id: number;
  log_date: string;
  habit_type: string;
  logged_value: number;
  unit: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface DailyProgress {
  date: string;
  habit_type: string;
  logged_value: number;
  target_value: number;
  completion_percentage: number;
  streak_days: number;
  is_goal_met: boolean;
}

export interface WeeklyProgress {
  week_start: string;
  week_end: string;
  habit_type: string;
  total_value: number;
  target_value: number;
  completion_percentage: number;
  days_met: number;
  total_days: number;
}

export interface MonthlyProgress {
  month: string;
  habit_type: string;
  total_value: number;
  target_value: number;
  completion_percentage: number;
  days_met: number;
  total_days: number;
}

export interface Feedback {
  habit_type: string;
  feedback_message: string;
  suggestions: string[];
  encouragement: string;
  completion_percentage: number;
  streak_days: number;
}

// User API
export const userApi = {
  create: (userData: any) => api.post<User>('/users/', userData),
  getAll: () => api.get<User[]>('/users/'),
  getById: (id: number) => api.get<User>(`/users/${id}`),
  update: (id: number, userData: any) => api.put<User>(`/users/${id}`, userData),
  delete: (id: number) => api.delete(`/users/${id}`),
};

// Questionnaire API
export const questionnaireApi = {
  create: (userId: number, data: Partial<Questionnaire>) => 
    api.post<Questionnaire>(`/users/${userId}/questionnaire`, data),
  get: (userId: number) => 
    api.get<Questionnaire>(`/users/${userId}/questionnaire`),
  update: (userId: number, data: Partial<Questionnaire>) => 
    api.put<Questionnaire>(`/users/${userId}/questionnaire`, data),
  delete: (userId: number) => 
    api.delete(`/users/${userId}/questionnaire`),
};

// Habit Target API
export const habitTargetApi = {
  create: (userId: number, data: Omit<HabitTarget, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => 
    api.post<HabitTarget>(`/users/${userId}/habit-targets`, data),
  getAll: (userId: number, habitType?: string) => 
    api.get<HabitTarget[]>(`/users/${userId}/habit-targets`, { 
      params: habitType ? { habit_type: habitType } : {} 
    }),
  getByType: (userId: number, habitType: string) => 
    api.get<HabitTarget>(`/users/${userId}/habit-targets/${habitType}`),
  update: (userId: number, habitType: string, data: Partial<HabitTarget>) => 
    api.put<HabitTarget>(`/users/${userId}/habit-targets/${habitType}`, data),
  delete: (userId: number, habitType: string) => 
    api.delete(`/users/${userId}/habit-targets/${habitType}`),
};

// Habit Log API
export const habitLogApi = {
  create: (userId: number, data: Omit<HabitLog, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => 
    api.post<HabitLog>(`/users/${userId}/habit-logs`, data),
  getAll: (userId: number, filters?: { habit_type?: string; start_date?: string; end_date?: string }) => 
    api.get<HabitLog[]>(`/users/${userId}/habit-logs`, { params: filters }),
  getByDateAndType: (userId: number, logDate: string, habitType: string) => 
    api.get<HabitLog>(`/users/${userId}/habit-logs/${logDate}/${habitType}`),
  update: (userId: number, logDate: string, habitType: string, data: Partial<HabitLog>) => 
    api.put<HabitLog>(`/users/${userId}/habit-logs/${logDate}/${habitType}`, data),
  delete: (userId: number, logDate: string, habitType: string) => 
    api.delete(`/users/${userId}/habit-logs/${logDate}/${habitType}`),
};

// Progress API
export const progressApi = {
  getDaily: (userId: number, targetDate: string, habitType: string) => 
    api.get<DailyProgress>(`/users/${userId}/progress/daily/${targetDate}/${habitType}`),
  getWeekly: (userId: number, weekStart: string, habitType: string) => 
    api.get<WeeklyProgress>(`/users/${userId}/progress/weekly/${weekStart}/${habitType}`),
  getMonthly: (userId: number, year: number, month: number, habitType: string) => 
    api.get<MonthlyProgress>(`/users/${userId}/progress/monthly/${year}/${month}/${habitType}`),
};

// Feedback API
export const feedbackApi = {
  get: (userId: number, habitType: string, days: number = 7) => 
    api.get<Feedback>(`/users/${userId}/feedback/${habitType}`, { 
      params: { days } 
    }),
};

export default api;
