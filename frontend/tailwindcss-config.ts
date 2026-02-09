import type { Config } from 'tailwindcss';

export default {
  content: ['./src/**/*.{html,ts}'],
  theme: {
    extend: {
      colors: {
        'emily-cream': '#F5EDE3',
        'emily-rose': '#D4A5A5',
        'emily-sage': '#A8B5A0',
        'emily-taupe': '#8B7F76',
        'emily-gold': '#C9A961',
      },
      fontFamily: {
        serif: ['Playfair Display', 'serif'],
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config;
