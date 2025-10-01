import { AppShell } from './ui/theme/AppShell'

export default function App (): JSX.Element {
  return (
    <AppShell>
      <main className="app-main">
        <section className="app-section">
          <h1>ProcureAI Frontend</h1>
          <p>
            This is the starting point for the ProcureAI SaaS UI. Components will be
            implemented incrementally following the design system.
          </p>
        </section>
      </main>
    </AppShell>
  )
}
