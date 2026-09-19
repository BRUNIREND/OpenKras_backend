export type ExcursionStatus = 'draft' | 'published';
export type MediaType = 'image' | 'audio';

export interface User {
  id: number;
  email: string;
  role: 'user' | 'admin';
}

export interface MediaObject {
  id: number;
  file_url: string;
  media_type: MediaType;
}

export interface Excursion {
  id: number;
  category_id: number | null;
  title: string;
  description: string | null;
  status: ExcursionStatus;
  created_at: string;
  distance: number,
  duration: number,
}

// Интерфейс для ответа при авторизации
export interface LoginResponse {
  access_token: string;
  token_type: string;
}


export interface PointContent {
  id?: number;
  lang: string;
  name: string;
  description: string | null;
  address: string | null;
  media_ids?: number[],
  audio?: MediaObject;
  images: MediaObject[];
}

export interface Point {
  id: number;
  latitude: number;
  longitude: number;
  radius_meters: number;
  position: number;
  contents: PointContent[];
}

export interface FullExcursion extends Excursion {
  points: Point[];
  images: MediaObject[];
  cover_url?: string;
}
export interface Category {
  id: number;
  name: string;
  slug: string;
}