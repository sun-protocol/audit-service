import { useEffect, useState } from 'react';
import { Plus, Pencil, Trash2, Play, Loader2 } from 'lucide-react';
import { fetchRepos, createRepo, updateRepo, deleteRepo, triggerScan } from '../api';
import type { Repository, RepoForm } from '../types';

const SKILL_OPTIONS = [
  { value: 'backend-server-scanner', label: 'backend-server-scanner' },
  { value: 'smart-contract-audit', label: 'smart-contract-audit' },
  { value: 'sun-frontend', label: 'sun-frontend' },
  { value: 'sunhat', label: 'sunhat' },
];

const emptyForm: RepoForm = {
  url: '',
  platform: 'github',
  branch: 'main',
  access_token: '',
  scan_prompt: '',
  skill: SKILL_OPTIONS[0].value,
};

export default function Repositories() {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<RepoForm>({ ...emptyForm });
  const [saving, setSaving] = useState(false);
  const [scanningId, setScanningId] = useState<number | null>(null);
  const [selectedRepoIds, setSelectedRepoIds] = useState<number[]>([]);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    fetchRepos()
      .then((items) => {
        setRepos(items);
        setSelectedRepoIds((prev) => prev.filter((id) => items.some((repo) => repo.id === id)));
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const openCreate = () => {
    setEditId(null);
    setForm({ ...emptyForm });
    setModalOpen(true);
  };

  const openEdit = (repo: Repository) => {
    setEditId(repo.id);
    setForm({
      url: repo.url,
      platform: repo.platform,
      branch: repo.branch,
      access_token: '',
      skill: repo.skill ?? SKILL_OPTIONS[0].value,
    });
    setModalOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const data = { ...form };
      if (!data.access_token) delete data.access_token;
      if (!data.skill) return;
      if (editId) {
        await updateRepo(editId, data);
      } else {
        await createRepo(data);
      }
      setModalOpen(false);
      load();
    } finally {
      setSaving(false);
    }
  };

  const toggleRepoSelected = (id: number) => {
    setSelectedRepoIds((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  };

  const toggleAllSelected = () => {
    setSelectedRepoIds((prev) => (prev.length === repos.length ? [] : repos.map((repo) => repo.id)));
  };

  const handleBatchScan = async () => {
    if (selectedRepoIds.length === 0) return;
    setScanningId(-1);
    try {
      for (const id of selectedRepoIds) {
        await triggerScan(id);
      }
      setSuccessMessage(`Successfully started audit for ${selectedRepoIds.length} ${selectedRepoIds.length === 1 ? 'repository' : 'repositories'}.`);
      load();
    } finally {
      setScanningId(null);
    }
  };

  const handleBatchDelete = async () => {
    if (selectedRepoIds.length === 0) return;
    if (!confirm(`Delete ${selectedRepoIds.length} repositories and all audit history?`)) return;
    for (const id of selectedRepoIds) {
      await deleteRepo(id);
    }
    setSelectedRepoIds([]);
    setSuccessMessage(`Successfully deleted ${selectedRepoIds.length} ${selectedRepoIds.length === 1 ? 'repository' : 'repositories'}.`);
    load();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-text-primary">Repositories</h1>
        <div className="flex items-center gap-3">
          <button
            onClick={handleBatchScan}
            disabled={selectedRepoIds.length === 0 || scanningId !== null}
            className="flex items-center gap-2 bg-green-50 hover:bg-green-100 text-green-700 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer disabled:opacity-50"
          >
            <Play className="w-4 h-4" /> Audit Selected
          </button>
          <button
            onClick={handleBatchDelete}
            disabled={selectedRepoIds.length === 0}
            className="flex items-center gap-2 bg-red-50 hover:bg-red-100 text-danger px-4 py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer disabled:opacity-50"
          >
            <Trash2 className="w-4 h-4" /> Delete Selected
          </button>
          <button
            onClick={openCreate}
            className="flex items-center gap-2 bg-primary hover:bg-primary-hover text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Add Repository
          </button>
        </div>
      </div>

      {successMessage && (
        <div className="mb-4 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm font-medium text-green-700">
          {successMessage}
        </div>
      )}

      {repos.length === 0 ? (
        <div className="bg-surface rounded-xl border border-border px-6 py-16 text-center">
          <p className="text-text-secondary">No repositories configured yet.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          <div className="flex items-center gap-3 px-1">
            <input
              type="checkbox"
              checked={repos.length > 0 && selectedRepoIds.length === repos.length}
              onChange={toggleAllSelected}
              className="w-4 h-4"
            />
            <span className="text-sm text-text-secondary">{selectedRepoIds.length} selected</span>
          </div>
          {repos.map((repo) => (
            <div key={repo.id} className="bg-surface rounded-xl border border-border p-5 flex items-center gap-5">
              <div className="shrink-0">
                <input
                  type="checkbox"
                  checked={selectedRepoIds.includes(repo.id)}
                  onChange={() => toggleRepoSelected(repo.id)}
                  className="w-4 h-4"
                />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-text-primary font-medium break-all">{repo.url}</p>
                <p className="text-xs text-text-secondary mt-1">
                  Branch: <span className="font-medium">{repo.branch}</span>
                  {repo.has_token && (
                    <span className="ml-2 text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-blue-100 text-blue-600">Token</span>
                  )}
                  {repo.skill && (
                    <span className="ml-2 text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-purple-100 text-purple-700">{repo.skill}</span>
                  )}
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => openEdit(repo)}
                  className="p-2 rounded-lg text-text-secondary hover:bg-surface-secondary transition-colors cursor-pointer"
                >
                  <Pencil className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-surface rounded-2xl shadow-2xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-5 border-b border-border">
              <h2 className="text-lg font-semibold text-text-primary">
                {editId ? 'Edit Repository' : 'Add Repository'}
              </h2>
            </div>
            <div className="px-6 py-5 space-y-4">
              <Field label="Repository URL" value={form.url} onChange={(v) => setForm({ ...form, url: v })} placeholder="https://github.com/user/repo.git" />
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-text-secondary mb-1.5">Platform</label>
                  <select
                    value={form.platform}
                    onChange={(e) => setForm({ ...form, platform: e.target.value as 'github' | 'gitlab' })}
                    className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-white text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/30"
                  >
                    <option value="github">GitHub</option>
                    <option value="gitlab">GitLab</option>
                  </select>
                </div>
                <Field label="Branch" value={form.branch} onChange={(v) => setForm({ ...form, branch: v })} placeholder="main" />
              </div>
              <Field
                label="Access Token"
                value={form.access_token ?? ''}
                onChange={(v) => setForm({ ...form, access_token: v })}
                placeholder={editId ? '(leave blank to keep current)' : 'ghp_xxxx or glpat-xxxx'}
                type="password"
              />
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1.5">Skill</label>
                <select
                  value={form.skill ?? ''}
                  onChange={(e) => setForm({ ...form, skill: e.target.value })}
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-white text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/30"
                >
                  {SKILL_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="px-6 py-4 border-t border-border flex justify-end gap-3">
              <button
                onClick={() => setModalOpen(false)}
                className="px-4 py-2 rounded-lg text-sm font-medium text-text-secondary hover:bg-surface-secondary transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving || !form.url || !form.skill}
                className="px-5 py-2 rounded-lg text-sm font-medium bg-primary hover:bg-primary-hover text-white transition-colors cursor-pointer disabled:opacity-50"
              >
                {saving ? 'Saving...' : editId ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({
  label, value, onChange, placeholder, type = 'text',
}: {
  label: string; value: string; onChange: (v: string) => void; placeholder?: string; type?: string;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-text-secondary mb-1.5">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-white text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/30"
      />
    </div>
  );
}
