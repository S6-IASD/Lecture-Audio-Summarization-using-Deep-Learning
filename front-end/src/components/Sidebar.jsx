import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  PlusCircle,
  User,
  LogOut,
  Sparkles,
} from 'lucide-react';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/create', label: 'Create Summary', icon: PlusCircle },
  { href: '/profile', label: 'Profile', icon: User },
];

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  return (
    <div
      className="fixed left-0 top-0 h-full w-60 bg-[#000000] flex flex-col z-50 border-r border-white/10"
      data-testid="sidebar"
    >
      {/* Logo */}
      <div className="px-6 py-8">
        <Link to="/dashboard" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 bg-[#1DB954] rounded-full flex items-center justify-center group-hover:animate-pulse-glow transition-shadow">
            <Sparkles className="w-4 h-4 text-black" />
          </div>
          <span className="text-white font-bold text-lg tracking-tight">SummarizR</span>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive =
            location.pathname === item.href ||
            location.pathname.startsWith(item.href + '/');
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              to={item.href}
              className={`
                flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-150 group relative
                ${isActive
                  ? 'text-white bg-white/10'
                  : 'text-[#B3B3B3] hover:text-white hover:bg-white/5'
                }
              `}
              data-testid={`nav-${item.href.replace('/', '')}`}
            >
              {/* Active indicator — 4px green left border */}
              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-[#1DB954] rounded-r-full" />
              )}
              <Icon
                className={`w-5 h-5 flex-shrink-0 transition-colors ${isActive ? 'text-[#1DB954]' : 'text-[#B3B3B3] group-hover:text-white'}`}
              />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="px-3 pb-6">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium text-[#B3B3B3] hover:text-white hover:bg-white/5 transition-all duration-150 w-full group"
          data-testid="button-logout"
        >
          <LogOut className="w-5 h-5 flex-shrink-0 group-hover:text-red-400 transition-colors" />
          <span>Log Out</span>
        </button>
      </div>
    </div>
  );
}
