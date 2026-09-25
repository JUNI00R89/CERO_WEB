import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/login': 'http://localhost:8000',
      '/usuarios': 'http://localhost:8000',
      '/cuentas': 'http://localhost:8000',
      '/categorias': 'http://localhost:8000',
      '/movimientos': 'http://localhost:8000',
      '/presupuestos': 'http://localhost:8000',
      '/metas-ahorro': 'http://localhost:8000',
    },
  },
})
