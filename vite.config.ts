import { defineConfig } from 'vite';

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    // Relative to the project root
    outDir: './static/dist',
    rollupOptions: {
      input: {
        // This is your CSS entry point
        styles: './static_src/src/input.css',
      },
      output: {
        // This will output a styles.css file
        assetFileNames: '[name].css'
      }
    },
  },
});
