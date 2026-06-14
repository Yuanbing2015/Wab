'use client';

import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Star, Trash2, Sparkles, Loader2 } from 'lucide-react';
import {
  getMistake,
  deleteMistake,
  genSolutionHint,
  updateMistake,
  type Mistake,
} from '@/lib/mistakes';
import SpeakButton from '@/components/SpeakButton';

export default function MistakeDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const mistakeId = Number(id);
  const router = useRouter();
  const [m, setM] = useState<Mistake | null>(null);
  const [hint, setHint] = useState('');
  const [loading, setLoading] = useState(true);
  const [genLoading, setGenLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getMistake(mistakeId)
      .then(setM)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [mistakeId]);

  async function onGenHint() {
    setGenLoading(true);
    try {
      const { content_md } = await genSolutionHint(mistakeId);
      setHint(content_md);
    } catch (e) {
      setError(e instanceof Error ? e.message : '生成失败');
    } finally {
      setGenLoading(false);
    }
  }

  async function onToggleGolden() {
    if (!m) return;
    const updated = await updateMistake(mistakeId, { is_golden: !m.is_golden });
    setM(updated);
  }

  async function onDelete() {
    if (!confirm('确定删除这道错题？')) return;
    await deleteMistake(mistakeId);
    router.push('/mistakes');
  }

  if (loading) return <p className="text-center text-slate-400 py-12">加载中...</p>;
  if (!m) return <p className="text-center text-red-500 py-12">{error || '错题不存在'}</p>;

  return (
    <main className="max-w-2xl mx-auto p-4 pb-12">
      <header className="flex items-center gap-3 py-4">
        <Link href="/mistakes" className="p-2 hover:bg-slate-100 rounded-xl">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <h1 className="text-2xl font-bold flex-1">错题详情</h1>
        <button onClick={onToggleGolden} className="p-2 hover:bg-slate-100 rounded-xl">
          <Star className={`w-6 h-6 ${m.is_golden ? 'text-amber-400 fill-amber-400' : 'text-slate-300'}`} />
        </button>
        <button onClick={onDelete} className="p-2 hover:bg-red-50 rounded-xl text-red-400">
          <Trash2 className="w-6 h-6" />
        </button>
      </header>

      {m.image_urls.length > 0 && (
        <img src={m.image_urls[0]} alt="错题原图" className="w-full rounded-2xl border mb-4" />
      )}

      <div className="bg-white rounded-2xl p-5 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <span className="text-xs px-2 py-0.5 bg-primary-50 text-primary-600 rounded-full">{m.subject}</span>
          {m.question_type && (
            <span className="text-xs px-2 py-0.5 bg-slate-100 text-slate-500 rounded-full">{m.question_type}</span>
          )}
          <span className="flex-1" />
          <SpeakButton text={m.stem_text} />
        </div>

        <div>
          <p className="text-xs text-slate-400 mb-1">题干</p>
          <p className="text-lg text-slate-800">{m.stem_text}</p>
        </div>

        {m.options.length > 0 && (
          <div className="space-y-1">
            {m.options.map((o, i) => (
              <p key={i} className="text-slate-600">{o}</p>
            ))}
          </div>
        )}

        <div className="grid grid-cols-2 gap-3">
          <div className="bg-emerald-50 rounded-xl p-3">
            <p className="text-xs text-emerald-500 mb-1">正确答案</p>
            <p className="text-emerald-700 font-medium">{m.correct_answer || '—'}</p>
          </div>
          <div className="bg-red-50 rounded-xl p-3">
            <p className="text-xs text-red-400 mb-1">孩子的答案</p>
            <p className="text-red-600 font-medium">{m.child_answer || '—'}</p>
          </div>
        </div>

        {m.error_hypothesis && (
          <div className="bg-amber-50 rounded-xl p-3">
            <p className="text-xs text-amber-500 mb-1">错因分析</p>
            <p className="text-amber-700">{m.error_hypothesis}</p>
          </div>
        )}

        {(m.error_tags.length > 0 || m.custom_tags.length > 0) && (
          <div className="flex flex-wrap gap-1">
            {m.error_tags.map((t) => (
              <span key={t} className="text-xs px-2 py-0.5 bg-red-50 text-red-500 rounded">{t}</span>
            ))}
            {m.custom_tags.map((t) => (
              <span key={t} className="text-xs px-2 py-0.5 bg-emerald-50 text-emerald-600 rounded">{t}</span>
            ))}
          </div>
        )}
      </div>

      {/* 解题思路 */}
      <div className="bg-white rounded-2xl p-5 shadow-sm mt-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-bold text-slate-800">解题思路</h2>
          <button
            onClick={onGenHint}
            disabled={genLoading}
            className="inline-flex items-center gap-1 text-sm text-primary-600 bg-primary-50 px-3 py-1.5 rounded-lg disabled:opacity-50"
          >
            {genLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            AI 生成
          </button>
        </div>
        {hint ? (
          <pre className="whitespace-pre-wrap text-slate-700 text-sm leading-relaxed">{hint}</pre>
        ) : (
          <p className="text-slate-400 text-sm">点击「AI 生成」获取分步骤解题思路</p>
        )}
      </div>
    </main>
  );
}
