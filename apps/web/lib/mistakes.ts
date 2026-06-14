/** 错题相关类型与 API */
import { apiGet, apiPost, apiPut, apiDelete, apiUpload } from './api';

export interface RecognizeResult {
  subject: string;
  grade_guess: string | null;
  question_type: string | null;
  stem: string;
  options: string[];
  correct_answer: string | null;
  child_answer: string | null;
  auto_tags: string[];
  error_hypothesis: string | null;
  solution_hint_draft: string | null;
  image_object_key: string | null;
}

export interface Mistake {
  id: number;
  subject: string;
  question_type: string | null;
  stem_text: string;
  options: string[];
  correct_answer: string | null;
  child_answer: string | null;
  grade: number | null;
  error_hypothesis: string | null;
  mastery_score: number;
  is_golden: boolean;
  status: string;
  error_tags: string[];
  custom_tags: string[];
  image_urls: string[];
  created_at: string;
}

export interface CreateMistakePayload {
  subject: string;
  question_type?: string | null;
  stem_text: string;
  options?: string[];
  correct_answer?: string | null;
  child_answer?: string | null;
  grade?: number | null;
  error_tags?: string[];
  custom_tags?: string[];
  solution_hint?: string | null;
  solution_url?: string | null;
  image_object_keys?: string[];
  is_golden?: boolean;
}

export function recognizeImage(file: File, gradeHint?: string) {
  return apiUpload<RecognizeResult>(
    '/mistakes/recognize',
    file,
    gradeHint ? { grade_hint: gradeHint } : undefined,
  );
}

export function createMistake(payload: CreateMistakePayload) {
  return apiPost<Mistake>('/mistakes', payload);
}

export function listMistakes(params: {
  subject?: string;
  grade?: number;
  keyword?: string;
  is_golden?: boolean;
} = {}) {
  const q = new URLSearchParams();
  if (params.subject) q.set('subject', params.subject);
  if (params.grade != null) q.set('grade', String(params.grade));
  if (params.keyword) q.set('keyword', params.keyword);
  if (params.is_golden != null) q.set('is_golden', String(params.is_golden));
  const qs = q.toString();
  return apiGet<Mistake[]>(`/mistakes${qs ? `?${qs}` : ''}`);
}

export function getMistake(id: number) {
  return apiGet<Mistake>(`/mistakes/${id}`);
}

export function updateMistake(id: number, payload: Partial<CreateMistakePayload>) {
  return apiPut<Mistake>(`/mistakes/${id}`, payload);
}

export function deleteMistake(id: number) {
  return apiDelete<void>(`/mistakes/${id}`);
}

export function genSolutionHint(id: number) {
  return apiPost<{ content_md: string }>(`/mistakes/${id}/solution-hint`, {});
}

export function synthesizeTTS(text: string) {
  return apiPost<{ url: string }>('/tts/synthesize', { text });
}
