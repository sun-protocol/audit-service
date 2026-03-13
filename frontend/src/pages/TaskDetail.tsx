import { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Loader2, Clock, Timer, Download } from 'lucide-react';
import { fetchTask, getAuditReportDownloadUrl } from '../api';
import type { TaskDetail as TaskDetailType } from '../types';
import StatusBadge from '../components/StatusBadge';

export default function TaskDetail() {
  const { id } = useParams<{ id: string }>();
  const [task, setTask] = useState<TaskDetailType | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!id) return;
    fetchTask(Number(id))
      .then(setTask)
      .finally(() => setLoading(false));
  }, [id]);

  // SSE for live logs if task is running/pending
  useEffect(() => {
    if (!task || (task.status !== 'running' && task.status !== 'pending')) return;

    const taskId = task.id;
    const evtSource = new EventSource(`/api/tasks/${taskId}/logs`);
    evtSource.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.log) {
        setLogs((prev) => [...prev, data.log]);
      }
      if (data.done) {
        evtSource.close();
        fetchTask(taskId).then(setTask);
      }
    };
    evtSource.onerror = () => {
      evtSource.close();
    };
    return () => evtSource.close();
  }, [task]);

  // Auto-scroll logs
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!task) {
    return <div className="text-text-secondary">Task not found.</div>;
  }

  const output = task.result?.raw_output ?? '';
  const hasLiveLog = task.status === 'running' || task.status === 'pending';
  const displayOutput = hasLiveLog ? logs.join('\n') : output;

  return (
    <div>
      <Link to="/" className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-primary mb-5 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </Link>

      <div className="flex items-center gap-4 mb-6">
        <h1 className="text-2xl font-bold text-text-primary">Scan #{task.id}</h1>
        <StatusBadge status={task.status} />
        {task.status === 'success' && (
          <a
            href={getAuditReportDownloadUrl(task.id)}
            className="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium bg-primary hover:bg-primary-hover text-white transition-colors"
          >
            <Download className="w-4 h-4" />
            Download Audit
          </a>
        )}
      </div>

      {/* Meta info */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <MetaCard label="Repository" value={task.repo_name ?? '-'} />
        <MetaCard label="Triggered By" value={task.triggered_by} />
        <MetaCard
          label="Started"
          value={task.started_at ? new Date(task.started_at).toLocaleString() : '-'}
          icon={<Clock className="w-4 h-4 text-text-secondary" />}
        />
        <MetaCard
          label="Duration"
          value={task.duration_seconds != null ? `${task.duration_seconds.toFixed(1)}s` : '-'}
          icon={<Timer className="w-4 h-4 text-text-secondary" />}
        />
      </div>

      {/* Summary */}
      {task.result?.summary && (
        <div className="bg-surface rounded-xl border border-border p-5 mb-6">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">Summary</h2>
          <p className="text-sm text-text-primary whitespace-pre-wrap">{task.result.summary}</p>
        </div>
      )}

      {/* Full output */}
      <div className="bg-surface rounded-xl border border-border overflow-hidden">
        <div className="px-5 py-3 border-b border-border flex items-center justify-between">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">Output</h2>
          {hasLiveLog && (
            <span className="flex items-center gap-1.5 text-xs text-blue-600">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500" />
              </span>
              Live
            </span>
          )}
        </div>
        <div
          ref={logRef}
          className="p-5 max-h-[600px] overflow-auto bg-slate-950 text-slate-200 font-mono text-xs leading-relaxed whitespace-pre-wrap"
        >
          {displayOutput || 'No output available.'}
        </div>
      </div>
    </div>
  );
}

function MetaCard({ label, value, icon }: { label: string; value: string; icon?: React.ReactNode }) {
  return (
    <div className="bg-surface rounded-xl border border-border p-4">
      <div className="flex items-center gap-1.5 mb-1">
        {icon}
        <span className="text-xs font-medium text-text-secondary uppercase tracking-wider">{label}</span>
      </div>
      <div className="text-sm font-semibold text-text-primary">{value}</div>
    </div>
  );
}
