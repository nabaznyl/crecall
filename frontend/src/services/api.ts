/**
 * API Client for crecall backend
 * 
 * Provides typed methods for interacting with the FastAPI backend.
 */

import axios from 'axios';
import type { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Types
export interface Clip {
  id: number;
  clip_id: string;
  session_id: number;
  name?: string;
  is_auto: boolean;
  content: Record<string, any>;
  working_directory?: string;
  git_branch?: string;
  git_commit?: string;
  git_dirty: boolean;
  created_at: string;
}

export interface ClipCreate {
  session_id: string;
  name?: string;
  is_auto?: boolean;
  content: Record<string, any>;
  working_directory?: string;
  git_branch?: string;
  git_commit?: string;
  git_dirty?: boolean;
}

export interface Memory {
  id: number;
  session_id: number;
  content: string;
  tags: string[];
  category?: string;
  importance: number;
  linked_clip_id?: number;
  linked_checkpoint_id?: number;
  created_at: string;
  updated_at: string;
}

export interface MemoryCreate {
  session_id: string;
  content: string;
  tags?: string[];
  category?: string;
  importance?: number;
  linked_clip_id?: number;
  linked_checkpoint_id?: number;
}

export interface MemoryUpdate {
  content?: string;
  tags?: string[];
  category?: string;
  importance?: number;
}

export interface Session {
  id: number;
  session_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface SessionCreate {
  session_id: string;
  status?: string;
}

export interface SessionSummary {
  session_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  clips_count: number;
  memories_count: number;
  checkpoints_count: number;
}

// API Methods

export const api = {
  // Health check
  async health(): Promise<{ status: string }> {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Clips
  clips: {
    async list(sessionId?: string, limit: number = 10): Promise<Clip[]> {
      const params = new URLSearchParams();
      if (sessionId) params.append('session_id', sessionId);
      params.append('limit', limit.toString());
      
      const response = await apiClient.get(`/api/clips?${params}`);
      return response.data;
    },

    async get(clipId: string): Promise<Clip> {
      const response = await apiClient.get(`/api/clips/${clipId}`);
      return response.data;
    },

    async create(data: ClipCreate): Promise<Clip> {
      const response = await apiClient.post('/api/clips', data);
      return response.data;
    },

    async delete(clipId: string): Promise<void> {
      await apiClient.delete(`/api/clips/${clipId}`);
    },

    async prune(keepLast: number = 100, olderThanDays?: number): Promise<{ deleted: number }> {
      const data: any = { keep_last: keepLast };
      if (olderThanDays) data.older_than_days = olderThanDays;
      
      const response = await apiClient.post('/api/clips/prune', data);
      return response.data;
    },
  },

  // Memories  
  memories: {
    async list(
      sessionId?: string,
      limit: number = 20,
      search?: string,
      tags?: string[]
    ): Promise<Memory[]> {
      const params = new URLSearchParams();
      if (sessionId) params.append('session_id', sessionId);
      params.append('limit', limit.toString());
      if (search) params.append('search', search);
      if (tags) tags.forEach(tag => params.append('tags', tag));
      
      const response = await apiClient.get(`/api/memories?${params}`);
      return response.data;
    },

    async get(memoryId: number): Promise<Memory> {
      const response = await apiClient.get(`/api/memories/${memoryId}`);
      return response.data;
    },

    async create(data: MemoryCreate): Promise<Memory> {
      const response = await apiClient.post('/api/memories', data);
      return response.data;
    },

    async update(memoryId: number, data: MemoryUpdate): Promise<Memory> {
      const response = await apiClient.put(`/api/memories/${memoryId}`, data);
      return response.data;
    },

    async delete(memoryId: number): Promise<void> {
      await apiClient.delete(`/api/memories/${memoryId}`);
    },

    async search(query: string, limit: number = 20): Promise<{ results: Memory[]; count: number }> {
      const response = await apiClient.post('/api/memories/search', null, {
        params: { query, limit },
      });
      return response.data;
    },
  },

  // Sessions
  sessions: {
    async list(limit: number = 50): Promise<Session[]> {
      const response = await apiClient.get('/api/sessions', {
        params: { limit },
      });
      return response.data;
    },

    async get(sessionId: string): Promise<Session> {
      const response = await apiClient.get(`/api/sessions/${sessionId}`);
      return response.data;
    },

    async create(data: SessionCreate): Promise<Session> {
      const response = await apiClient.post('/api/sessions', data);
      return response.data;
    },

    async update(sessionId: string, status: string): Promise<Session> {
      const response = await apiClient.put(`/api/sessions/${sessionId}`, { status });
      return response.data;
    },

    async delete(sessionId: string): Promise<void> {
      await apiClient.delete(`/api/sessions/${sessionId}`);
    },

    async getSummary(sessionId: string): Promise<SessionSummary> {
      const response = await apiClient.get(`/api/sessions/${sessionId}/summary`);
      return response.data;
    },
  },
};

export default api;
