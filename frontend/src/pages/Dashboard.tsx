import { useEffect, useRef, useState } from 'react';
import { Activity, GitFork, CheckCircle2, XCircle, Loader2, Download, Trash2, X } from 'lucide-react';
import { fetchDashboardStats, fetchTasks, fetchTask, fetchQueueStatus, getAuditReportDownloadUrl, deleteTask } from '../api';
import type { DashboardStats, QueueStatus, ScanTask } from '../types';
import StatusBadge from '../components/StatusBadge';

function formatBrowserLocalDateTime(value: string) {
  const normalizedValue =
    /(?:Z|[+-]\d{2}:\d{2})$/.test(value) ? value : `${value}Z`;
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  }).format(new Date(normalizedValue));
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [queueStatus, setQueueStatus] = useState<QueueStatus | null>(null);
  const [recentTasks, setRecentTasks] = useState<ScanTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTaskId, setActiveTaskId] = useState<number | null>(null);
  const [isLogsOpen, setIsLogsOpen] = useState(false);
  const [liveLogs, setLiveLogs] = useState<string[]>([]);
  const logRef = useRef<HTMLDivElement>(null);

  const loadDashboard = () => {
    return Promise.all([fetchDashboardStats(), fetchTasks({ limit: 10 }), fetchQueueStatus()]).then(([s, t, q]) => {
      setStats(s);
      setRecentTasks(t);
      setQueueStatus(q);
      setActiveTaskId((prev) => {
        const stillActive = prev != null && t.some((task) => task.id === prev);
        if (stillActive) return prev;
        if (prev != null) {
          setLiveLogs([]);
          setIsLogsOpen(false);
        }
        return null;
      });
    });
  };

  useEffect(() => {
    loadDashboard().finally(() => setLoading(false));
  }, []);

  const handleDeleteTask = async (taskId: number) => {
    if (!confirm('Delete this task?')) return;
    await deleteTask(taskId);
    setRecentTasks((prev) => prev.filter((task) => task.id !== taskId));
    if (activeTaskId === taskId) {
      setActiveTaskId(null);
      setIsLogsOpen(false);
      setLiveLogs([]);
    }
    loadDashboard();
  };

  const openTaskOutput = (taskId: number, status: ScanTask['status']) => {
    setActiveTaskId(taskId);
    setIsLogsOpen(true);
    setLiveLogs([]);
    if (status === 'running' || status === 'pending') {
      return;
    }
    fetchTask(taskId).then((task) => {
      setLiveLogs(task.result?.raw_output ? task.result.raw_output.split('\n') : []);
    });
  };

  useEffect(() => {
    if (activeTaskId == null || !isLogsOpen) {
      return;
    }

    const evtSource = new EventSource(`/api/tasks/${activeTaskId}/logs`);
    evtSource.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.log) {
        setLiveLogs((prev) => [...prev, data.log]);
      }
      if (data.done) {
        evtSource.close();
        loadDashboard();
        fetchTask(activeTaskId).then((task) => {
          if (task.result?.raw_output) {
            setLiveLogs(task.result.raw_output.split('\n'));
          }
        });
      }
    };
    evtSource.onerror = () => {
      evtSource.close();
    };
    return () => evtSource.close();
  }, [activeTaskId, isLogsOpen]);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [liveLogs]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  const cards = stats
    ? [
        { label: 'Total Repos', value: stats.total_repos, icon: GitFork, color: 'text-primary' },
        { label: 'Successful', value: stats.success_count, icon: CheckCircle2, color: 'text-success' },
        { label: 'Failed', value: stats.failed_count, icon: XCircle, color: 'text-danger' },
        { label: 'Running', value: stats.running_count, icon: Activity, color: 'text-warning' },
      ]
    : [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-text-primary mb-6">Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        {cards.map((c) => (
          <div key={c.label} className="bg-surface rounded-xl border border-border p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-text-secondary uppercase tracking-wider">{c.label}</span>
              <c.icon className={`w-5 h-5 ${c.color}`} />
            </div>
            <div className="text-2xl font-bold text-text-primary">{c.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-surface rounded-xl border border-border p-5 mb-8">
        <h2 className="text-base font-semibold text-text-primary mb-4">Queue</h2>
        {queueStatus?.running ? (
          <div className="mb-4">
            <div className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-1">Running</div>
            <div className="text-sm text-text-primary break-all">{queueStatus.running.repo_url}</div>
          </div>
        ) : (
          <div className="mb-4 text-sm text-text-secondary">No running task.</div>
        )}
        <div>
          <div className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-1">Queued</div>
          {queueStatus && queueStatus.queued.length > 0 ? (
            <div className="space-y-2">
              {queueStatus.queued.map((item, index) => (
                <div key={`${item.repo_id}-${index}`} className="text-sm text-text-primary break-all">
                  {item.repo_url}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-text-secondary">Queue is empty.</div>
          )}
        </div>
      </div>

      <div className="bg-surface rounded-xl border border-border">
        <div className="px-6 py-4 border-b border-border">
          <h2 className="text-base font-semibold text-text-primary">Recent Scans</h2>
        </div>
        {recentTasks.length === 0 ? (
          <div className="px-6 py-12 text-center text-text-secondary text-sm">
            No scans yet. Add a repository and trigger a scan.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-text-secondary text-xs uppercase tracking-wider">
                <th className="px-6 py-3 font-medium">Started</th>
                <th className="px-6 py-3 font-medium">Repository</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Duration</th>
                <th className="px-6 py-3 font-medium">Audit</th>
                <th className="px-6 py-3 font-medium">Delete</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {recentTasks.map((task) => (
                <tr key={task.id} className="hover:bg-surface-secondary transition-colors">
                  <td className="px-6 py-3 text-text-secondary">
                    {task.started_at ? formatBrowserLocalDateTime(task.started_at) : '-'}
                  </td>
                  <td className="px-6 py-3 text-text-primary font-medium max-w-[360px] truncate">{task.repo_url ?? '-'}</td>
                  <td className="px-6 py-3">
                    <StatusBadge status={task.status} />
                    {(task.status === 'running' || task.status === 'pending' || task.status === 'failed') && (
                      <button
                        onClick={() => openTaskOutput(task.id, task.status)}
                        className="ml-3 text-primary hover:underline font-medium"
                      >
                        {task.status === 'failed' ? 'View output' : 'View logs'}
                      </button>
                    )}
                  </td>
                  <td className="px-6 py-3 text-text-secondary">
                    {task.duration_seconds != null ? `${task.duration_seconds.toFixed(1)}s` : '-'}
                  </td>
                  <td className="px-6 py-3">
                    {task.status === 'success' ? (
                      <a
                        href={getAuditReportDownloadUrl(task.id)}
                        className="inline-flex items-center gap-1.5 text-primary hover:underline font-medium"
                      >
                        <Download className="w-4 h-4" />
                        Download
                      </a>
                    ) : (
                      <span className="text-text-secondary">-</span>
                    )}
                  </td>
                  <td className="px-6 py-3">
                    <button
                      onClick={() => handleDeleteTask(task.id)}
                      className="inline-flex items-center gap-1.5 text-danger hover:underline font-medium"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {isLogsOpen && activeTaskId != null && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4"
          onClick={() => setIsLogsOpen(false)}
        >
          <div
            className="w-full max-w-6xl bg-surface rounded-xl border border-border overflow-hidden shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-5 py-3 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-3">
                <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
                  Task Output #{activeTaskId}
                </h2>
                {recentTasks.find((task) => task.id === activeTaskId)?.status && ['running', 'pending'].includes(recentTasks.find((task) => task.id === activeTaskId)!.status) && (
                  <span className="flex items-center gap-1.5 text-xs text-blue-600">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75" />
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500" />
                    </span>
                    Live
                  </span>
                )}
              </div>
              <button
                onClick={() => setIsLogsOpen(false)}
                className="inline-flex items-center justify-center rounded-md p-2 text-text-secondary hover:bg-surface-secondary hover:text-text-primary"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div
              ref={logRef}
              className="p-5 h-[70vh] overflow-auto bg-slate-950 text-slate-200 font-mono text-xs leading-relaxed whitespace-pre-wrap"
            >
              {liveLogs.join('\n') || 'Waiting for logs...'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
