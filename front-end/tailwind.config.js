/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        spotify: {
          green: '#1DB954',
          'green-hover': '#1aa34a',
          black: '#121212',
          card: '#1A1A1A',
          hover: '#282828',
          sidebar: '#000000',
          'text-primary': '#FFFFFF',
          'text-secondary': '#B3B3B3',
          'text-muted': '#535353',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
