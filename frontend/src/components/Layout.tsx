import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, GitFork, Shield } from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/repos', icon: GitFork, label: 'Repositories' },
];

export default function Layout() {
  return (
    <div className="flex h-screen bg-surface-secondary">
      {/* Sidebar */}
      <aside className="w-60 bg-sidebar flex flex-col shrink-0">
        <div className="flex items-center gap-2.5 px-5 py-5">
          <Shield className="w-7 h-7 text-primary" />
          <span className="text-white font-semibold text-lg tracking-tight">Audit Service</span>
        </div>
        <nav className="flex-1 px-3 mt-2 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary text-white'
                    : 'text-slate-400 hover:bg-sidebar-hover hover:text-white'
                }`
              }
            >
              <item.icon className="w-[18px] h-[18px]" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-5 py-4 text-xs text-slate-500">v1.0.0</div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8 max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
