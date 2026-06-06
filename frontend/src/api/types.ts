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
  topic: string;
  topic_label: string;
  has_video: boolean;
  video_provider: string | null;
  video_url: string | null;
  video_embed_url: string | null;
  comment_count: number;
  can_view_body: boolean;
  author_id: number;
  author_label: string;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: number;
  author_id: number;
  author_label: string;
  text: string;
  created_at: string;
  can_delete: boolean;
}

export interface AuthorSummary {
  id: number;
  label: string;
  post_count: number;
  paid_count: number;
  free_count: number;
}

export interface TopicSummary {
  slug: string;
  label: string;
  post_count: number;
}

export interface UserProfile {
  id: number;
  phone: string;
  display_name: string;
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
