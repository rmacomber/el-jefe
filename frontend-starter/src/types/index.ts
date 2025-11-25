// Core data types for the El Jefe Dashboard

export interface AgentJob {
  job_id: string;
  agent_type: string;
  task: string;
  status: AgentStatus;
  started_at: string;
  completed_at?: string;
  progress: number;
  current_step: string;
  workspace: string;
  error_message?: string;
  tokens_used: number;
  words_generated: number;
}

export type AgentStatus = 'running' | 'completed' | 'failed' | 'paused';

export interface WorkflowSession {
  session_id: string;
  goal: string;
  status: WorkflowStatus;
  started_at: string;
  completed_at?: string;
  total_steps: number;
  completed_steps: number;
  current_step: number;
  agents_used: string[];
  workspace: string;
  metrics: Record<string, any>;
}

export type WorkflowStatus = 'running' | 'completed' | 'failed' | 'paused';

export interface ChatMessage {
  message_id: string;
  sender: 'user' | 'el-jefe';
  content: string;
  timestamp: string;
  message_type: MessageType;
}

export type MessageType = 'text' | 'status' | 'error' | 'system';

export interface SystemStatus {
  status: string;
  uptime: string;
  active_agents: number;
  active_workflows: number;
  connected_clients: number;
}

export interface SystemMetrics {
  total_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  running_jobs: number;
  total_workflows: number;
  completed_workflows: number;
  total_tokens: number;
  total_words: number;
  average_completion_time: number;
}

// WebSocket message types
export interface WebSocketMessage {
  type: WebSocketMessageType;
  data?: any;
  job?: AgentJob;
  session?: WorkflowSession;
  message?: ChatMessage;
  session_id?: string;
  success?: boolean;
}

export type WebSocketMessageType =
  | 'agent_update'
  | 'workflow_update'
  | 'initial_data'
  | 'workflow_interrupted'
  | 'workflow_paused'
  | 'workflow_resumed'
  | 'chat_message'
  | 'file_update';

// UI State types
export interface UIState {
  theme: ThemeMode;
  sidebarOpen: boolean;
  activeTab: string;
  notifications: Notification[];
  loading: Record<string, boolean>;
  searchQuery: string;
  filters: Filters;
}

export type ThemeMode = 'light' | 'dark' | 'auto';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  autoHide?: boolean;
}

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface Filters {
  agents: {
    status: AgentStatus[];
    type: string[];
  };
  workflows: {
    status: WorkflowStatus[];
    workspace: string[];
  };
  dateRange: {
    start: string | null;
    end: string | null;
  };
}

// Component props interfaces
export interface MetricCardProps {
  title: string;
  value: number | string;
  change?: number;
  changeType?: 'increase' | 'decrease';
  icon?: React.ReactNode;
  loading?: boolean;
  className?: string;
}

export interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'warning' | 'error';
  pulse?: boolean;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

export interface AgentListItemProps {
  agent: AgentJob;
  onAction?: (action: string, agentId: string) => void;
  className?: string;
}

export interface WorkflowCardProps {
  workflow: WorkflowSession;
  onAction?: (action: string, sessionId: string) => void;
  className?: string;
}

export interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

export interface ChatMessageProps {
  message: ChatMessage;
  className?: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Configuration types
export interface DashboardConfig {
  refreshInterval: number;
  maxRetries: number;
  enableNotifications: boolean;
  enableSoundEffects: boolean;
  defaultViewMode: 'grid' | 'list';
  enableAutoRefresh: boolean;
}

// User preferences
export interface UserPreferences {
  theme: ThemeMode;
  sidebarCollapsed: boolean;
  notifications: {
    enabled: boolean;
    types: NotificationType[];
    sound: boolean;
  };
  dashboard: {
    defaultTab: string;
    refreshInterval: number;
    showInactiveItems: boolean;
  };
}

// Error types
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
  stack?: string;
}

// Search and filtering
export interface SearchFilters {
  query: string;
  agents: {
    types: string[];
    status: AgentStatus[];
  };
  workflows: {
    status: WorkflowStatus[];
    workspaces: string[];
  };
  dateRange: {
    start: Date | null;
    end: Date | null;
  };
}

// Chart data types
export interface ChartDataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

export interface TimeSeriesData {
  name: string;
  data: ChartDataPoint[];
  color?: string;
}

// Performance metrics
export interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  apiResponseTime: number;
  memoryUsage: number;
  errorRate: number;
}