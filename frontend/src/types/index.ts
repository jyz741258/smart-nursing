export interface UserInfo {
  id: number
  phone: string
  name: string
  gender: number | null
  age: number | null
  id_card: string | null
  address: string | null
  avatar: string | null
  emergency_contact: string | null
  emergency_phone: string | null
  user_type: number
}

export interface LoginForm {
  phone: string
  password: string
}

export interface RegisterForm {
  phone: string
  password: string
  sms_code: string
  user_type: number
  name?: string
  gender?: number
  age?: number
}

export interface Elder {
  id: number
  name: string
  gender: number | null
  age: number | null
  address: string | null
  avatar: string | null
  emergency_contact?: string
  emergency_phone?: string
}

export interface NursingRecord {
  id: number
  elder_id: number
  elder_name: string | null
  nursing_type: number
  nursing_type_name: string
  description: string
  start_time: string | null
  end_time: string | null
  status: number
  status_name: string
  staff_id: number
  staff_name: string | null
  notes: string | null
  created_at: string
}

export interface HealthMetric {
  id: number
  elder_id: number
  elder_name: string | null
  metric_type: number
  metric_type_name: string
  metric_value: number
  unit: string
  recorded_at: string
  notes: string | null
}

export interface CarePlan {
  id: number
  elder_id: number
  elder_name: string | null
  title: string
  description: string
  start_date: string | null
  end_date: string | null
  status: number
  status_name: string
  tasks: CareTask[]
  created_at: string
}

export interface CareTask {
  id: number
  care_plan_id: number
  task_name: string
  task_type: number
  description: string
  frequency: string
  scheduled_time: string | null
  status: number
  status_name: string
  completed_at: string | null
  completed_by: number | null
  notes: string | null
}

export interface Notification {
  id: number
  user_id: number
  title: string
  content: string
  notification_type: number
  notification_type_name: string
  priority: number
  priority_name: string
  is_read: boolean
  created_at: string
  read_at: string | null
}

export interface DashboardStats {
  today_nursing_count: number
  today_completed_tasks: number
  elder_count: number
  staff_count: number
  pending_tasks: number
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
}

export interface PageResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}