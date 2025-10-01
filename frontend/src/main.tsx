import React from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { AppRoutes } from './routes'
import { ThemeProvider } from './ui/theme/ThemeProvider'
import App from './App'
import './styles/global.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

const root = document.getElementById('root')!

createRoot(root).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AppRoutes />
      </ThemeProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>
)
