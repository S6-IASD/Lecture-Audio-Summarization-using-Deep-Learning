import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Sparkles, Eye, EyeOff } from 'lucide-react';
import api from '@/api/axios';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function Login() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [form, setForm] = useState({ username: '', password: '' });
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!form.username.trim()) errs.username = "Username is required";
    if (!form.password) errs.password = 'Password is required';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    try {
      const response = await api.post('/api/auth/login/', {
        username: form.username,
        password: form.password,
      });

      const { access, refresh } = response.data.tokens;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      toast.success('Login successful!');
      navigate('/dashboard');
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.non_field_errors?.[0] ||
        'Invalid credentials';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#121212] flex items-center justify-center px-4">
      {/* Decorative glows */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#1DB954]/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-[#1DB954]/3 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-sm relative z-10 animate-fade-in-up">
        {/* Logo */}
        <div className="flex flex-col items-center mb-10">
          <div className="w-14 h-14 bg-[#1DB954] rounded-full flex items-center justify-center mb-4 shadow-lg shadow-[#1DB954]/20">
            <Sparkles className="w-7 h-7 text-black" />
          </div>
          <h1 className="text-white text-3xl font-bold tracking-tight">SummarizR</h1>
          <p className="text-[#B3B3B3] text-sm mt-1">Sign in to your account</p>
        </div>

        {/* Card */}
        <div className="bg-[#1A1A1A] rounded-2xl p-8 border border-white/5 shadow-2xl shadow-black/50">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-white text-sm font-medium mb-2" htmlFor="login-username">
                Username
              </label>
              <input
                id="login-username"
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
              <label className="block text-white text-sm font-medium mb-2" htmlFor="login-password">
                Password
              </label>
              <div className="relative">
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  autoComplete="current-password"
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

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-[#1DB954] text-black font-bold py-3 rounded-full text-sm hover:bg-[#1aa34a] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-2 hover:scale-[1.02] active:scale-[0.98]"
              data-testid="button-submit"
            >
              {isLoading ? (
                <>
                  <LoadingSpinner size="sm" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-[#B3B3B3] text-sm mt-6">
          Don't have an account yet?{' '}
          <Link
            to="/register"
            className="text-white font-semibold hover:text-[#1DB954] transition-colors"
            data-testid="link-register"
          >
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}
