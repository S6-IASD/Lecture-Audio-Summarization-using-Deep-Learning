import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Sparkles, Eye, EyeOff } from 'lucide-react';
import api from '@/api/axios';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function Register() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [form, setForm] = useState({ username: '', email: '', password: '', password_confirm: '' });
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (form.username.length < 3) errs.username = 'At least 3 characters';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = 'Invalid email';
    if (form.password.length < 6) errs.password = 'At least 6 characters';
    if (form.password !== form.password_confirm) errs.password_confirm = 'Passwords do not match';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    try {
      await api.post('/api/auth/register/', {
        username: form.username,
        email: form.email,
        password: form.password,
        password_confirm: form.password_confirm,
      });

      // Auto-login after register
      const loginResponse = await api.post('/api/auth/login/', {
        username: form.username,
        password: form.password,
      });

      const { access, refresh } = loginResponse.data.tokens;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch (err) {
      const data = err.response?.data;
      const firstError = data
        ? Object.values(data)[0]?.[0]
        : undefined;
      toast.error(firstError || 'Error creating account');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#121212] flex items-center justify-center px-4">
      {/* Decorative glows */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/3 right-1/3 w-96 h-96 bg-[#1DB954]/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/3 left-1/3 w-64 h-64 bg-[#1DB954]/3 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-sm relative z-10 animate-fade-in-up">
        {/* Logo */}
        <div className="flex flex-col items-center mb-10">
          <div className="w-14 h-14 bg-[#1DB954] rounded-full flex items-center justify-center mb-4 shadow-lg shadow-[#1DB954]/20">
            <Sparkles className="w-7 h-7 text-black" />
          </div>
          <h1 className="text-white text-3xl font-bold tracking-tight">SummarizR</h1>
          <p className="text-[#B3B3B3] text-sm mt-1">Create your free account</p>
        </div>

        {/* Card */}
        <div className="bg-[#1A1A1A] rounded-2xl p-8 border border-white/5 shadow-2xl shadow-black/50">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-white text-sm font-medium mb-2" htmlFor="reg-username">
                Username
              </label>
              <input
                id="reg-username"
                type="text"
                placeholder="your_name"
                autoComplete="username"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                className="w-full bg-[#282828] text-white placeholder-[#535353] rounded-lg px-4 py-3 text-sm border border-transparent focus:border-[#1DB954] transition-colors"
                data-testid="input-username"
              />
              {errors.username && (
                <p className="text-red-400 text-xs mt-1">{errors.username}</p>
              )}
            </div>

            <div>
              <label className="block text-white text-sm font-medium mb-2" htmlFor="reg-email">
                Email address
              </label>
              <input
                id="reg-email"
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full bg-[#282828] text-white placeholder-[#535353] rounded-lg px-4 py-3 text-sm border border-transparent focus:border-[#1DB954] transition-colors"
                data-testid="input-email"
              />
              {errors.email && (
                <p className="text-red-400 text-xs mt-1">{errors.email}</p>
              )}
            </div>

            <div>
              <label className="block text-white text-sm font-medium mb-2" htmlFor="reg-password">
                Password
              </label>
              <div className="relative">
                <input
                  id="reg-password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  autoComplete="new-password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  className="w-full bg-[#282828] text-white placeholder-[#535353] rounded-lg px-4 py-3 pr-11 text-sm border border-transparent focus:border-[#1DB954] transition-colors"
                  data-testid="input-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#B3B3B3] hover:text-white transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && (
                <p className="text-red-400 text-xs mt-1">{errors.password}</p>
              )}
            </div>

            <div>
              <label className="block text-white text-sm font-medium mb-2" htmlFor="reg-password-confirm">
                Confirm password
              </label>
              <div className="relative">
                <input
                  id="reg-password-confirm"
                  type={showPasswordConfirm ? 'text' : 'password'}
                  placeholder="••••••••"
                  autoComplete="new-password"
                  value={form.password_confirm}
                  onChange={(e) => setForm({ ...form, password_confirm: e.target.value })}
                  className="w-full bg-[#282828] text-white placeholder-[#535353] rounded-lg px-4 py-3 pr-11 text-sm border border-transparent focus:border-[#1DB954] transition-colors"
                  data-testid="input-password-confirm"
                />
                <button
                  type="button"
                  onClick={() => setShowPasswordConfirm(!showPasswordConfirm)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#B3B3B3] hover:text-white transition-colors"
                  tabIndex={-1}
                >
                  {showPasswordConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password_confirm && (
                <p className="text-red-400 text-xs mt-1">{errors.password_confirm}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-[#1DB954] text-black font-bold py-3 rounded-full text-sm hover:bg-[#1aa34a] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-2 hover:scale-[1.02] active:scale-[0.98]"
              data-testid="button-submit"
            >
              {isLoading ? (
                <>
                  <LoadingSpinner size="sm" />
                  Creating...
                </>
              ) : (
                'Create account'
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-[#B3B3B3] text-sm mt-6">
          Already have an account?{' '}
          <Link
            to="/login"
            className="text-white font-semibold hover:text-[#1DB954] transition-colors"
            data-testid="link-login"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
