'use client';

import { useState, useRef } from 'react';
import { Volume2, Loader2 } from 'lucide-react';
import { synthesizeTTS } from '@/lib/mistakes';

/** 朗读按钮（一年级友好，大喇叭图标）— D-01 底层能力 */
export default function SpeakButton({ text }: { text: string }) {
  const [loading, setLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  async function speak() {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const { url } = await synthesizeTTS(text);
      if (!audioRef.current) audioRef.current = new Audio();
      audioRef.current.src = url;
      await audioRef.current.play();
    } catch {
      // 降级：浏览器原生 TTS
      if ('speechSynthesis' in window) {
        const u = new SpeechSynthesisUtterance(text);
        u.lang = 'zh-CN';
        u.rate = 0.9;
        window.speechSynthesis.speak(u);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={speak}
      disabled={loading}
      className="inline-flex items-center gap-1 px-3 py-2 bg-primary-50 text-primary-600 rounded-xl hover:bg-primary-100 transition disabled:opacity-50"
      title="听题"
    >
      {loading ? (
        <Loader2 className="w-5 h-5 animate-spin" />
      ) : (
        <Volume2 className="w-5 h-5" />
      )}
      <span className="text-sm font-medium">听题</span>
    </button>
  );
}
