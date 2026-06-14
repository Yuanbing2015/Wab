'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Star, Search, Camera } from 'lucide-react';
import { listMistakes, type Mistake } from '@/lib/mistakes';

const SUBJECTS = ['全部', '数学', '语文', '英语', '科学'];

export default function MistakesPage() {
  const [mistakes, setMistakes] = useState<Mistake[]>([]);
  const [loading, setLoading] = useState(true);
  const [subject, setSubject] = useState('全部');
  const [keyword, setKeyword] = useState('');
  const [error, setError] = useState('');

  async function load() {
    setLoading(true);
    setError('');
    try {
      const data = await listMistakes({
        subject: subject === '全部' ? undefined : subject,
        keyword: keyword || undefined,
      });
      setMistakes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [subject]);

  return (
    <main className="max-w-2xl mx-auto p-4 pb-24">
      <header className="flex items-center gap-3 py-4">
        <Link href="/" className="p-2 hover:bg-slate-100 rounded-xl">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <h1 className="text-2xl font-bold flex-1">错题库</h1>
        <span className="text-sm text-slate-400">{mistakes.length} 题</span>
      </header>

      {/* 搜索 */}
      <div className="flex gap-2 mb-3">
        <div className="flex-1 flex items-center bg-white border border-slate-200 rounded-xl px-3">
          <Search className="w-5 h-5 text-slate-400" />
          <input
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && load()}
            placeholder="搜索题干..."
            className="flex-1 px-2 py-2.5 outline-none"
          />
        </div>
        <button onClick={load} className="px-4 bg-primary text-white rounded-xl">
          搜索
        </button>
      </div>

      {/* 学科筛选 */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
        {SUBJECTS.map((s) => (
          <button
            key={s}
            onClick={() => setSubject(s)}
            className={`px-4 py-1.5 rounded-full whitespace-nowrap text-sm ${
              subject === s
                ? 'bg-primary text-white'
                : 'bg-white text-slate-600 border border-slate-200'
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {error && <p className="text-red-500 bg-red-50 px-4 py-3 rounded-xl">{error}</p>}

      {loading ? (
        <p className="text-center text-slate-400 py-12">加载中...</p>
      ) : mistakes.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <p className="mb-4">还没有错题</p>
          <Link href="/capture" className="text-primary font-medium">
            去录入第一道 →
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {mistakes.map((m) => (
            <Link
              key={m.id}
              href={`/mistakes/${m.id}`}
              className="block bg-white rounded-2xl p-4 shadow-sm hover:shadow-md transition"
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs px-2 py-0.5 bg-primary-50 text-primary-600 rounded-full">
                  {m.subject}
                </span>
                {m.question_type && (
                  <span className="text-xs px-2 py-0.5 bg-slate-100 text-slate-500 rounded-full">
                    {m.question_type}
                  </span>
                )}
                {m.is_golden && <Star className="w-4 h-4 text-amber-400 fill-amber-400" />}
                <span className="flex-1" />
                <span className="text-xs text-slate-400">
                  {new Date(m.created_at).toLocaleDateString()}
                </span>
              </div>
              <p className="text-slate-800 line-clamp-2">{m.stem_text}</p>
              {(m.error_tags.length > 0 || m.custom_tags.length > 0) && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {m.error_tags.map((t) => (
                    <span key={t} className="text-xs px-2 py-0.5 bg-red-50 text-red-500 rounded">
                      {t}
                    </span>
                  ))}
                  {m.custom_tags.map((t) => (
                    <span key={t} className="text-xs px-2 py-0.5 bg-emerald-50 text-emerald-600 rounded">
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}

      {/* 悬浮录入按钮 */}
      <Link
        href="/capture"
        className="fixed bottom-6 right-6 w-16 h-16 bg-primary text-white rounded-full shadow-lg shadow-primary/30 flex items-center justify-center hover:bg-primary-600 transition"
      >
        <Camera className="w-7 h-7" />
      </Link>
    </main>
  );
}
