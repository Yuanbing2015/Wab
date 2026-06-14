'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiPost } from '@/lib/api';

interface RegisterResponse {
  access_token: string;
  user: {
    id: number;
    name: string;
    role: string;
  };
}

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [grade, setGrade] = useState('一年级');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await apiPost<RegisterResponse>('/auth/register', {
        name,
        password,
        role: 'kid',
        current_grade: grade,
      });
      localStorage.setItem('wab_token', data.access_token);
      localStorage.setItem('wab_user', JSON.stringify(data.user));
      router.push('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : '注册失败');
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
        <h1 className="text-3xl font-bold text-center mb-8">📓 注册账号</h1>

        <label className="block mb-4">
          <span className="text-sm font-medium text-slate-700">小朋友的名字</span>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="mt-2 block w-full px-4 py-3 border border-slate-200 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </label>

        <label className="block mb-4">
          <span className="text-sm font-medium text-slate-700">密码</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={4}
            className="mt-2 block w-full px-4 py-3 border border-slate-200 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </label>

        <label className="block mb-6">
          <span className="text-sm font-medium text-slate-700">年级</span>
          <select
            value={grade}
            onChange={(e) => setGrade(e.target.value)}
            className="mt-2 block w-full px-4 py-3 border border-slate-200 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-primary bg-white"
          >
            {['幼儿园', '一年级', '二年级', '三年级', '四年级', '五年级', '六年级'].map(
              (g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ),
            )}
          </select>
        </label>

        {error && (
          <p className="text-red-500 text-sm mb-4 bg-red-50 px-3 py-2 rounded-lg">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-primary text-white rounded-xl hover:bg-primary-600 transition text-lg font-medium disabled:opacity-50"
        >
          {loading ? '注册中...' : '注册'}
        </button>

        <p className="text-center mt-6 text-sm text-slate-500">
          已有账号？
          <Link href="/login" className="text-primary hover:underline ml-1">
            登录
          </Link>
        </p>
      </form>
    </main>
  );
}
