import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../services/api'
import { OfferCard } from '../../components/buyer/negotiation/OfferCard'
import { NegotiationFeed } from '../../components/buyer/negotiation/NegotiationFeed'
import { NegotiationControl } from '../../components/buyer/negotiation/NegotiationControl'
import { SmartAlert } from '../../components/shared/SmartAlert'
import type { NegotiationSession } from '../../types'

export function NegotiationTheater (): JSX.Element {
  const { requestId } = useParams<{ requestId: string }>()

  const { data: sessions, isLoading } = useQuery({
    queryKey: ['negotiations', requestId],
    queryFn: () => api.getNegotiationsForRequest(requestId!),
    enabled: Boolean(requestId),
  })

  if (isLoading) {
    return <div className="py-12 text-center text-sm text-[var(--core-color-text-muted)]">Loading negotiation insights…</div>
  }

  if (!sessions || sessions.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-[var(--core-color-text-primary)]">Negotiation theater</h1>
        <SmartAlert
          severity="info"
          title="No negotiations in progress"
          message="Launch AI sourcing to start negotiating with vendors."
        />
      </div>
    )
  }

  const activeSessions = sessions.filter((session) => session.status === 'active')
  const topSessions = activeSessions.slice(0, 3)

  const getStatus = (index: number): 'leading' | 'contender' | 'fallback' => {
    if (index === 0) return 'leading'
    if (index === 1) return 'contender'
    return 'fallback'
  }

  return (
    <div className="space-y-8">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold text-[var(--core-color-text-primary)]">Negotiation theater</h1>
        <p className="text-sm text-[var(--core-color-text-muted)]">Watch your agent orchestrate offers in real-time. Intervene when needed.</p>
      </header>

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-[var(--core-color-text-primary)]">Current best offers</h2>
          <p className="text-sm text-[var(--core-color-text-muted)]">AI ranks offers based on budget fit, feature coverage, and risk.</p>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {topSessions.map((session, index) => (
            <OfferCard key={session.session_id} session={session} rank={index + 1} status={getStatus(index)} />
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-[var(--core-color-text-primary)]">Live negotiation feed</h2>
          <p className="text-sm text-[var(--core-color-text-muted)]">Reasoning transparency for every move across active vendors.</p>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          {activeSessions.map((session: NegotiationSession) => (
            <NegotiationFeed key={session.session_id} session={session} />
          ))}
        </div>
      </section>

      <NegotiationControl
        onAdjustBudget={() => console.log('adjust budget')}
        onAddRequirement={() => console.log('add requirement')}
        onStop={() => console.log('pause negotiations')}
        onAcceptBest={() => console.log('accept best offer')}
      />
    </div>
  )
}
