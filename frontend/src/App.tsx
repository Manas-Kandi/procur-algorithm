import { Suspense } from 'react'
import { AppRoutes } from './routes'

export default function App (): JSX.Element {
  return (
    <Suspense fallback={<div className="app-loading">Loading ProcureAI…</div>}>
      <AppRoutes />
    </Suspense>
  )
}
