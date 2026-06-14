import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '错题银行',
  description: '一个父亲为孩子手作的、可生长 12 年的家庭学习陪伴系统',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="antialiased bg-slate-50 min-h-screen">{children}</body>
    </html>
  );
}
