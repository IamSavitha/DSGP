import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Lock, Mail } from 'lucide-react';
import { adminLogin } from '../api/admin';
import { useAuth } from '../context/AuthContext';

const AdminLoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login: authLogin } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
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
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-16rem)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-semibold text-slate-700 tracking-tight">Admin Sign In</h1>
          <p className="mt-2 text-sm text-slate-500">
            Sign in to access the admin dashboard
          </p>
        </div>

        <form className="mt-8 space-y-6 bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-lg border border-slate-100" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-600 mb-1.5">
                Email address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-slate-300" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
                  placeholder="admin@kayak.com"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-600 mb-1.5">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-300" />
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 border-2 border-slate-300 rounded-xl text-slate-900 placeholder-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-400"
                  placeholder="••••••••"
                />
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-slate-400 to-red-400 hover:from-slate-500 hover:to-red-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-slate-500">
              Don't have an admin account?{' '}
              <Link to="/admin/signup" className="font-medium text-slate-600 hover:text-slate-700">
                Sign up
              </Link>
            </p>
            <p className="mt-2 text-sm text-slate-500">
              <Link to="/login" className="font-medium text-slate-600 hover:text-slate-700">
                User Login
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AdminLoginPage;

