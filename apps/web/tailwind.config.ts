import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#5B8DEF',
          50: '#EBF1FE',
          100: '#D7E3FD',
          500: '#5B8DEF',
          600: '#3B6FD8',
          700: '#2754B8',
        },
      },
      fontFamily: {
        sans: ['system-ui', 'PingFang SC', 'Microsoft YaHei', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

export default config;
