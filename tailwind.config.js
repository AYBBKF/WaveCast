/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#141414',
        card: '#1A1A1A',
        'card-hover': '#2A2A2A',
        primary: '#FFFFFF',
        'primary-focus': '#F0F0F0',
        accent: '#E50914',
      },
      keyframes: {
        glow: {
          '0%, 100%': { boxShadow: '0 0 5px #fff, 0 0 10px #fff, 0 0 15px #0077ff, 0 0 20px #0077ff' },
          '50%': { boxShadow: '0 0 10px #fff, 0 0 15px #0077ff, 0 0 20px #0077ff, 0 0 25px #0077ff' },
        }
      },
      animation: {
        glow: 'glow 2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
