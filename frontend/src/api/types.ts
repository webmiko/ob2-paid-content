/** Типы ответов JSON API. */

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Post {
  id: number;
  title: string;
  body: string | null;
  is_paid: boolean;
  can_view_body: boolean;
  author_id: number;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: number;
  phone: string;
  subscription_active: boolean;
}

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface PaymentCreateResponse {
  id: number;
  status: string;
  payment_url: string;
  amount: number;
  currency: string;
  created_at: string;
}

export interface PaymentSuccessResponse {
  status: string;
  subscription_active: boolean;
}

export interface ApiErrorBody {
  detail?: string;
  [key: string]: unknown;
}
