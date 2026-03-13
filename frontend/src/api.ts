import type { DashboardStats, QueueStatus, RepoForm, Repository, ScanTask, TaskDetail } from './types';

const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Repos
export const fetchRepos = () => request<Repository[]>('/repos');
export const fetchRepo = (id: number) => request<Repository>(`/repos/${id}`);
export const createRepo = (data: RepoForm) =>
  request<Repository>('/repos', { method: 'POST', body: JSON.stringify(data) });
export const updateRepo = (id: number, data: Partial<RepoForm>) =>
  request<Repository>(`/repos/${id}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteRepo = (id: number) =>
  request<void>(`/repos/${id}`, { method: 'DELETE' });
export const triggerScan = (repoId: number) =>
  request<{ task_id: number; message: string }>(`/repos/${repoId}/scan`, { method: 'POST' });

// Tasks
export const fetchTasks = (params?: { repo_id?: number; status?: string; limit?: number }) => {
  const qs = new URLSearchParams();
  if (params?.repo_id) qs.set('repo_id', String(params.repo_id));
  if (params?.status) qs.set('status', params.status);
  if (params?.limit) qs.set('limit', String(params.limit));
  const q = qs.toString();
  return request<ScanTask[]>(`/tasks${q ? `?${q}` : ''}`);
};
export const fetchTask = (id: number) => request<TaskDetail>(`/tasks/${id}`);
export const deleteTask = (id: number) => request<void>(`/tasks/${id}`, { method: 'DELETE' });
export const getAuditReportDownloadUrl = (taskId: number) => `${BASE}/tasks/${taskId}/audit-report`;

// Dashboard
export const fetchDashboardStats = () => request<DashboardStats>('/dashboard/stats');
export const fetchQueueStatus = () => request<QueueStatus>('/dashboard/queue');
