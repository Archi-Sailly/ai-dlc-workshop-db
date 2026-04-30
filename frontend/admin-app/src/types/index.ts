// === Enums ===

export enum OrderStatus {
  PENDING = 'PENDING',
  ACCEPTED = 'ACCEPTED',
  PREPARING = 'PREPARING',
  COMPLETED = 'COMPLETED',
}

export enum SessionStatus {
  ACTIVE = 'ACTIVE',
  COMPLETED = 'COMPLETED',
}

export enum SSEEventType {
  ORDER_CREATED = 'order_created',
  ORDER_STATUS_CHANGED = 'order_status_changed',
  ORDER_DELETED = 'order_deleted',
  SESSION_COMPLETED = 'session_completed',
  HEARTBEAT = 'heartbeat',
}

export enum SSEConnectionStatus {
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
}

// === Auth (백엔드 스키마 매칭) ===

export interface LoginRequest {
  store_identifier: string;
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
  store_id: string;
  username: string;
  display_name: string;
}

export interface TokenVerifyResponse {
  valid: boolean;
  store_id: string | null;
  username: string | null;
  expires_at: string | null;
}

// === Table / Session ===

export interface Table {
  id: string;
  store_id: string;
  table_number: number;
  is_active: boolean;
  created_at: string;
  url?: string;
}

export interface Session {
  id: string;
  store_id: string;
  table_id: string;
  started_at: string;
  completed_at?: string;
}

// === Order ===

export interface OrderItem {
  id: string;
  menu_id: string | null;
  menu_name: string;
  unit_price: number;
  quantity: number;
  subtotal: number;
}

export interface Order {
  id: string;
  store_id: string;
  table_id: string;
  session_id: string;
  order_number: number;
  status: OrderStatus;
  total_amount: number;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

// === Dashboard (백엔드 TableOrderSummary) ===

export interface DashboardTable {
  table_id: string;
  table_number: number;
  total_amount: number;
  order_count: number;
  latest_orders: Order[];
  has_new_order: boolean;
}

export interface DashboardResponse {
  tables: DashboardTable[];
}

// === Menu ===

export interface Category {
  id: string;
  store_id: string;
  name: string;
  sort_order: number;
  created_at: string;
}

export interface Menu {
  id: string;
  store_id: string;
  category_id: string;
  name: string;
  price: number;
  description?: string;
  image_url?: string;
  sort_order: number;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

export interface MenuDetail extends Menu {
  category_name?: string;
}

// === Pagination ===

export interface OrderHistoryItem {
  id: string;
  order_number: number;
  table_number: number;
  status: OrderStatus;
  total_amount: number;
  items: OrderItem[];
  created_at: string;
  session_completed_at?: string;
}

export interface OrderHistoryResponse {
  orders: OrderHistoryItem[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}

// === SSE Events ===

export interface SSEEvent<T = unknown> {
  event_type: string;
  store_id: string;
  table_number: number;
  data: T;
}

// === Toast ===

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}
