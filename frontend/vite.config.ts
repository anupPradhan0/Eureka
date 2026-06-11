import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // listen on 0.0.0.0 so the container is reachable from the host
    watch: {
      // Bind-mounted files in Docker don't emit native FS events reliably;
      // polling makes hot-module-reload work inside the container.
      usePolling: true,
    },
  },
})
