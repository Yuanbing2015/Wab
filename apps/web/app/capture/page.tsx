'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Camera, Loader2, Check, ArrowLeft } from 'lucide-react';
import {
  recognizeImage,
  createMistake,
  type RecognizeResult,
} from '@/lib/mistakes';
import SpeakButton from '@/components/SpeakButton';

const SUBJECTS = ['数学', '语文', '英语', '科学', '物理', '化学', '生物'];

function gradeToNum(g: string | null): number | null {
  if (!g) return null;
  const map: Record<string, number> = {
    一年级: 1, 二年级: 2, 三年级: 3, 四年级: 4, 五年级: 5, 六年级: 6,
    初一: 7, 初二: 8, 初三: 9, 高一: 10, 高二: 11, 高三: 12,
  };
  for (const [k, v] of Object.entries(map)) if (g.includes(k)) return v;
  return null;
}

export default function CapturePage() {
  const router = useRouter();
  const [preview, setPreview] = useState<string | null>(null);
  const [recognizing, setRecognizing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [draft, setDraft] = useState<RecognizeResult | null>(null);
  const [error, setError] = useState('');

  // 可编辑字段
  const [subject, setSubject] = useState('数学');
  const [stem, setStem] = useState('');
  const [correct, setCorrect] = useState('');
  const [childAns, setChildAns] = useState('');
  const [errorTags, setErrorTags] = useState('');
  const [customTags, setCustomTags] = useState('');
  const [solution, setSolution] = useState('');
  const [imageKey, setImageKey] = useState<string | null>(null);

  async function onSelectFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError('');
    setPreview(URL.createObjectURL(file));
    setRecognizing(true);
    try {
      const r = await recognizeImage(file);
      setDraft(r);
      setSubject(r.subject || '数学');
      setStem(r.stem || '');
      setCorrect(r.correct_answer || '');
      setChildAns(r.child_answer || '');
      setErrorTags(r.error_hypothesis || '');
      setCustomTags((r.auto_tags || []).join('、'));
      setSolution(r.solution_hint_draft || '');
      setImageKey(r.image_object_key);
    } catch (err) {
      setError(err instanceof Error ? err.message : '识别失败');
    } finally {
      setRecognizing(false);
    }
  }

  async function onSave() {
    setSaving(true);
    setError('');
    try {
      await createMistake({
        subject,
        stem_text: stem,
        correct_answer: correct,
        child_answer: childAns,
        grade: gradeToNum(draft?.grade_guess ?? null),
        question_type: draft?.question_type ?? null,
        options: draft?.options ?? [],
        error_tags: errorTags ? errorTags.split(/[、,，]/).map((s) => s.trim()).filter(Boolean) : [],
        custom_tags: customTags ? customTags.split(/[、,，]/).map((s) => s.trim()).filter(Boolean) : [],
        solution_hint: solution || null,
        image_object_keys: imageKey ? [imageKey] : [],
      });
      router.push('/mistakes');
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="max-w-2xl mx-auto p-4 pb-24">
      <header className="flex items-center gap-3 py-4">
        <Link href="/" className="p-2 hover:bg-slate-100 rounded-xl">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <h1 className="text-2xl font-bold">录入错题</h1>
      </header>

      {/* 拍照/选图 */}
      {!draft && (
        <label className="block">
          <div className="border-2 border-dashed border-primary-200 rounded-3xl p-12 text-center cursor-pointer hover:bg-primary-50 transition">
            {recognizing ? (
              <div className="flex flex-col items-center gap-3 text-primary-600">
                <Loader2 className="w-12 h-12 animate-spin" />
                <p className="text-lg">AI 正在识别错题...</p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3 text-slate-500">
                <Camera className="w-16 h-16 text-primary" />
                <p className="text-lg font-medium text-slate-700">拍照 / 选择错题图片</p>
                <p className="text-sm">支持手机拍照，AI 自动识别题目</p>
              </div>
            )}
          </div>
          <input
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={onSelectFile}
            disabled={recognizing}
          />
        </label>
      )}

      {error && (
        <p className="text-red-500 bg-red-50 px-4 py-3 rounded-xl my-4">{error}</p>
      )}

      {/* 识别结果可编辑 */}
      {draft && (
        <div className="space-y-4">
          {preview && (
            <img
              src={preview}
              alt="错题"
              className="w-full rounded-2xl border border-slate-200"
            />
          )}

          <div className="bg-white rounded-2xl p-4 shadow-sm space-y-4">
            <p className="text-sm text-primary-600 bg-primary-50 px-3 py-2 rounded-lg">
              ✨ AI 已识别，请快速核对后保存
            </p>

            <Field label="学科">
              <select
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="input"
              >
                {SUBJECTS.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </Field>

            <Field label="题干" extra={<SpeakButton text={stem} />}>
              <textarea
                value={stem}
                onChange={(e) => setStem(e.target.value)}
                rows={3}
                className="input"
              />
            </Field>

            <div className="grid grid-cols-2 gap-3">
              <Field label="正确答案">
                <input value={correct} onChange={(e) => setCorrect(e.target.value)} className="input" />
              </Field>
              <Field label="孩子的答案">
                <input value={childAns} onChange={(e) => setChildAns(e.target.value)} className="input" />
              </Field>
            </div>

            <Field label="错因标签（顿号分隔）">
              <input value={errorTags} onChange={(e) => setErrorTags(e.target.value)} className="input" placeholder="如：进位忘加" />
            </Field>

            <Field label="知识点 / 自定义标签（顿号分隔）">
              <input value={customTags} onChange={(e) => setCustomTags(e.target.value)} className="input" placeholder="如：几何题、逻辑题" />
            </Field>

            <Field label="解题思路">
              <textarea value={solution} onChange={(e) => setSolution(e.target.value)} rows={4} className="input" />
            </Field>
          </div>
        </div>
      )}

      {/* 底部保存栏 */}
      {draft && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4 flex gap-3 max-w-2xl mx-auto">
          <button
            onClick={() => { setDraft(null); setPreview(null); }}
            className="flex-1 py-3 border border-slate-200 rounded-xl text-slate-600"
          >
            重拍
          </button>
          <button
            onClick={onSave}
            disabled={saving}
            className="flex-[2] py-3 bg-primary text-white rounded-xl font-medium flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {saving ? <Loader2 className="w-5 h-5 animate-spin" /> : <Check className="w-5 h-5" />}
            保存入库
          </button>
        </div>
      )}

      <style jsx global>{`
        .input {
          margin-top: 0.5rem;
          display: block;
          width: 100%;
          padding: 0.625rem 0.875rem;
          border: 1px solid rgb(226 232 240);
          border-radius: 0.75rem;
          font-size: 1rem;
          background: white;
        }
        .input:focus {
          outline: none;
          box-shadow: 0 0 0 2px #5b8def;
        }
      `}</style>
    </main>
  );
}

function Field({
  label,
  children,
  extra,
}: {
  label: string;
  children: React.ReactNode;
  extra?: React.ReactNode;
}) {
  return (
    <label className="block">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-700">{label}</span>
        {extra}
      </div>
      {children}
    </label>
  );
}
