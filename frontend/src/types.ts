export interface Repository {
  id: number;
  name: string;
  url: string;
  platform: 'github' | 'gitlab';
  branch: string;
  has_token: boolean;
  scan_prompt: string | null;
  skill: string | null;
  created_at: string;
  updated_at: string;
}

export interface RepoForm {
  url: string;
  platform: 'github' | 'gitlab';
  branch: string;
  access_token?: string;
  scan_prompt?: string;
  skill?: string;
}

export interface ScanTask {
  id: number;
  repo_id: number;
  repo_name: string | null;
  repo_url: string | null;
  status: 'pending' | 'running' | 'success' | 'failed';
  started_at: string | null;
  finished_at: string | null;
  duration_seconds: number | null;
}

export interface ScanResult {
  id: number;
  task_id: number;
  raw_output: string | null;
  summary: string | null;
  created_at: string;
}

export interface TaskDetail extends ScanTask {
  result: ScanResult | null;
}

export interface DashboardStats {
  total_repos: number;
  enabled_repos: number;
  total_scans: number;
  scans_this_month: number;
  success_count: number;
  failed_count: number;
  running_count: number;
}

export interface QueueItem {
  repo_id: number;
  repo_url: string;
  triggered_by: string;
}

export interface QueueStatus {
  running: QueueItem | null;
  queued: QueueItem[];
}
