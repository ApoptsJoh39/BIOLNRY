/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static_src/**/*.{js,ts,jsx,tsx}',
    './src/**/*.{js,ts,jsx,tsx}', // Para archivos React/Vite
    './frontend/**/*.{js,ts,jsx,tsx}', // Si usas otra estructura
    './**/templates/**/*.html' // Rutas adicionales
  ],
  theme: {
    extend: {},
    extend: {
      colors: {
        'vino': {
          'light': '#A8324A',     // Un tono más claro, como afrutado
          'DEFAULT': '#800020',   // El clásico color Borgoña/vino
          'dark': '#5B0016',      // Un tono de vino profundo y oscuro
        },
      }
    },
  },
  plugins: [],
}