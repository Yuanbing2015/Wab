'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Camera, BookOpen, LogOut } from 'lucide-react';
import { getToken } from '@/lib/api';

export default function HomePage() {
  const router = useRouter();
  const [name, setName] = useState('');

  useEffect(() => {
    if (!getToken()) {
      router.push('/login');
      return;
    }
    try {
      const u = JSON.parse(localStorage.getItem('wab_user') || '{}');
      setName(u.name || '');
    } catch {
      /* ignore */
    }
  }, [router]);

  function logout() {
    localStorage.removeItem('wab_token');
    localStorage.removeItem('wab_user');
    router.push('/login');
  }

  return (
    <main className="max-w-2xl mx-auto p-4 min-h-screen">
      <header className="flex items-center justify-between py-6">
        <div>
          <p className="text-slate-400 text-sm">欢迎回来</p>
          <h1 className="text-2xl font-bold">{name || '小朋友'} 📓</h1>
        </div>
        <button onClick={logout} className="p-2 text-slate-400 hover:bg-slate-100 rounded-xl">
          <LogOut className="w-5 h-5" />
        </button>
      </header>

      <div className="grid grid-cols-2 gap-4 mt-4">
        <Link
          href="/capture"
          className="bg-primary text-white rounded-3xl p-6 flex flex-col items-center gap-3 shadow-lg shadow-primary/20 hover:scale-105 transition"
        >
          <Camera className="w-12 h-12" />
          <span className="text-lg font-medium">录入错题</span>
        </Link>
        <Link
          href="/mistakes"
          className="bg-white border border-slate-200 rounded-3xl p-6 flex flex-col items-center gap-3 hover:scale-105 transition"
        >
          <BookOpen className="w-12 h-12 text-primary" />
          <span className="text-lg font-medium text-slate-700">错题库</span>
        </Link>
      </div>

      <div className="mt-8 bg-white rounded-3xl p-6 text-center text-slate-400">
        <p className="text-sm">复习功能开发中 🚧</p>
        <p className="text-xs mt-1">翻牌 · 家庭对战 · 兴趣化剧情题即将上线</p>
      </div>
    </main>
  );
}
