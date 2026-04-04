/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          'deep-teal': '#003235',
          'emerald': '#008C6F',
          'mint': '#63D2B7',
          'forest': '#10645C',
          'light-gray': '#D3D3D3',
          'light-bg': '#F5F7FA',
          'near-black': '#1A1A1A',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
