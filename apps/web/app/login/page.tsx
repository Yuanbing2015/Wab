'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiPost } from '@/lib/api';

interface LoginResponse {
  access_token: string;
  user: {
    id: number;
    name: string;
    role: string;
    theme: string | null;
  };
}

export default function LoginPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await apiPost<LoginResponse>('/auth/login', {
        name,
        password,
      });
      localStorage.setItem('wab_token', data.access_token);
      localStorage.setItem('wab_user', JSON.stringify(data.user));
      router.push('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-3xl shadow-xl w-full max-w-md"
      >
        <h1 className="text-3xl font-bold text-center mb-2">📓 错题银行</h1>
        <p className="text-center text-slate-500 mb-8 text-sm">登录开始今天的复习</p>

        <label className="block mb-4">
          <span className="text-sm font-medium text-slate-700">小朋友的名字</span>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            autoComplete="username"
            className="mt-2 block w-full px-4 py-3 border border-slate-200 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="请输入"
          />
        </label>

        <label className="block mb-6">
          <span className="text-sm font-medium text-slate-700">密码</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            className="mt-2 block w-full px-4 py-3 border border-slate-200 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </label>

        {error && (
          <p className="text-red-500 text-sm mb-4 bg-red-50 px-3 py-2 rounded-lg">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-primary text-white rounded-xl hover:bg-primary-600 transition text-lg font-medium disabled:opacity-50 shadow-lg shadow-primary/20"
        >
          {loading ? '登录中...' : '登录'}
        </button>

        <p className="text-center mt-6 text-sm text-slate-500">
          没有账号？
          <Link
            href="/register"
            className="text-primary hover:underline ml-1"
          >
            注册
          </Link>
        </p>
      </form>
    </main>
  );
}
