import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Lock, Mail, User, Shield } from 'lucide-react';
import { login } from '../api/auth';
import { adminLogin } from '../api/admin';
import { useAuth } from '../context/AuthContext';

type LoginType = 'user' | 'admin';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login: authLogin } = useAuth();
  const [loginType, setLoginType] = useState<LoginType>('user');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (loginType === 'user') {
        const response = await login({ email, password });

        if (!response || !response.access_token || !response.user) {
          throw new Error('Invalid response from server');
        }

        // Update auth context with token and user
        authLogin(response.access_token, response.user);

        // Small delay to ensure state is updated before navigation
        setTimeout(() => {
          navigate('/');
        }, 100);
      } else {
        // Admin login
        const response = await adminLogin({ email, password });

        if (!response || !response.access_token || !response.admin) {
          throw new Error('Invalid response from server');
        }

        // Store admin token and info separately from user auth
        localStorage.setItem('admin_token', response.access_token);
        localStorage.setItem('admin', JSON.stringify(response.admin));
        localStorage.setItem('is_admin', 'true');

        // Update auth context (for navigation purposes)
        authLogin(response.access_token, {
          user_id: response.admin.admin_id,
          first_name: response.admin.first_name,
          last_name: response.admin.last_name,
          email: response.admin.email,
          phone_number: response.admin.phone_number,
          is_active: response.admin.is_active,
          created_at: response.admin.created_at,
          updated_at: response.admin.updated_at
        });

        // Navigate to admin dashboard
        setTimeout(() => {
          navigate('/admin');
        }, 100);
      }
    } catch (err: any) {
      // Handle nested error detail structure
      let errorMessage = 'Invalid email or password';
      if (err.message) {
        errorMessage = err.message;
      } else if (err.detail) {
        errorMessage = typeof err.detail === 'string' ? err.detail : err.detail.message || errorMessage;
      }
      setError(errorMessage);
      console.error('Login error:', err);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-16rem)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-semibold text-slate-900 tracking-tight">Sign In</h1>
          <p className="mt-2 text-sm text-slate-600">
            Choose your account type to continue
          </p>
        </div>

        {/* Login Type Selector */}
        <div className="flex space-x-2 bg-slate-100 p-1 rounded-lg">
          <button
            type="button"
            onClick={() => {
              setLoginType('user');
              setError('');
            }}
            className={`flex-1 flex items-center justify-center space-x-2 py-2.5 px-4 rounded-md font-medium text-sm transition-all ${
              loginType === 'user'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <User size={18} />
            <span>User</span>
          </button>
          <button
            type="button"
            onClick={() => {
              setLoginType('admin');
              setError('');
            }}
            className={`flex-1 flex items-center justify-center space-x-2 py-2.5 px-4 rounded-md font-medium text-sm transition-all ${
              loginType === 'admin'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Shield size={18} />
            <span>Admin</span>
          </button>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1.5">
                Email address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-slate-400" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-1.5">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-400" />
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
                  placeholder="••••••••"
                />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-slate-900 focus:ring-slate-900 border-slate-300 rounded"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-600">
                Remember me
              </label>
            </div>

            <div className="text-sm">
              <Link to="/forgot-password" className="font-medium text-slate-900 hover:text-slate-700">
                Forgot password?
              </Link>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-slate-900 hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>

          <div className="text-center space-y-2">
            {loginType === 'user' ? (
              <p className="text-sm text-slate-600">
                Don't have an account?{' '}
                <Link to="/signup" className="font-medium text-slate-900 hover:text-slate-700">
                  Sign up
                </Link>
              </p>
            ) : (
              <p className="text-sm text-slate-600">
                Don't have an admin account?{' '}
                <Link to="/admin/signup" className="font-medium text-slate-900 hover:text-slate-700">
                  Admin Sign up
                </Link>
              </p>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
