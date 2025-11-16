/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/*.html'
  ],
  theme: {
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