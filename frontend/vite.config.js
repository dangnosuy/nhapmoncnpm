import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const rootDir = fileURLToPath(new URL('.', import.meta.url))

function routeAliases() {
  return {
    name: 'route-aliases',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (req.url === '/client') {
          res.statusCode = 302
          res.setHeader('Location', '/client/')
          res.end()
          return
        }
        if (req.url === '/staff') {
          res.statusCode = 302
          res.setHeader('Location', '/staff/')
          res.end()
          return
        }
        next()
      })
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), routeAliases()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5000'
    }
  },
  build: {
    rollupOptions: {
      input: {
        main: resolve(rootDir, 'index.html'),
        client: resolve(rootDir, 'client/index.html'),
        staff: resolve(rootDir, 'staff/index.html')
      }
    }
  }
})
