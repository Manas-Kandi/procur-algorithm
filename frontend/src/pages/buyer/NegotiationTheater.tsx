import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../services/api'
import { Card } from '../../components/shared/Card'
import { Button } from '../../components/shared/Button'
import { AIExplainer } from '../../components/shared/AIExplainer'
import type { NegotiationSession } from '../../types'

export function NegotiationTheater() {
  const { requestId } = useParams<{ requestId: string }>()

  const { data: sessions, isLoading } = useQuery({
    queryKey: ['negotiations', requestId],
    queryFn: () => api.getNegotiationsForRequest(requestId!),
    enabled: !!requestId,
  })

  if (isLoading) {
    return <div className="p-6">Loading negotiations...</div>
  }

  const activeSessions = sessions?.filter(s => s.status === 'active') || []
  const topSessions = activeSessions.slice(0, 3)

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Negotiation Theater</h1>
        <p className="text-gray-600 mt-1">Watch your AI agent negotiate with vendors in real-time</p>
      </div>

      {/* Top Offers */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Best Offers</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {topSessions.map((session, idx) => (
            <VendorOfferCard key={session.session_id} session={session} rank={idx + 1} />
          ))}
        </div>
      </div>

      {/* Live Negotiation Feed */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Live Negotiation Feed</h2>
        <div className="space-y-4">
          {activeSessions.map((session) => (
            <NegotiationFeed key={session.session_id} session={session} />
          ))}
        </div>
      </div>

      {/* Control Panel */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Control Panel</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Button variant="outline" fullWidth>
            Adjust Budget Ceiling
          </Button>
          <Button variant="outline" fullWidth>
            Add Requirements
          </Button>
          <Button variant="danger" fullWidth>
            Stop All Negotiations
          </Button>
          <Button variant="primary" fullWidth>
            Accept Best Offer
          </Button>
        </div>
      </Card>
    </div>
  )
}

function VendorOfferCard({ session, rank }: { session: NegotiationSession; rank: number }) {
  const bestOffer = session.best_offer
  const latestMessage = session.messages[session.messages.length - 1]

  return (
    <Card className="relative">
      <div className="absolute -top-3 -right-3 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
        #{rank}
      </div>
      
      <div className="space-y-3">
        <div>
          <h3 className="font-semibold text-gray-900">Vendor {session.vendor_id.slice(0, 8)}</h3>
          <p className="text-sm text-gray-600">Round {session.current_round}</p>
        </div>

        {bestOffer && (
          <>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                ${bestOffer.components.unit_price.toFixed(2)}
                <span className="text-sm text-gray-600 font-normal">/seat/year</span>
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {bestOffer.components.term_months} month term • {bestOffer.components.payment_terms}
              </p>
            </div>

            <div className="pt-3 border-t border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-gray-600">Utility Score</span>
                <span className="text-xs font-bold text-gray-900">
                  {(bestOffer.score.utility * 100).toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${bestOffer.score.utility * 100}%` }}
                />
              </div>
            </div>

            <AIExplainer
              title="this offer was recommended"
              reasoning={[
                { label: 'Price vs Budget', value: `${((bestOffer.components.unit_price / 1200) * 100).toFixed(0)}% of ceiling` },
                { label: 'Feature Match', value: `${(bestOffer.score.spec_match * 100).toFixed(0)}%` },
                { label: 'Risk Level', value: 'Low' },
                { label: 'Total Value', value: `$${(bestOffer.components.unit_price * bestOffer.components.quantity).toLocaleString()}` },
              ]}
            />
          </>
        )}
      </div>
    </Card>
  )
}

function NegotiationFeed({ session }: { session: NegotiationSession }) {
  const latestMessages = session.messages.slice(-3).reverse()

  return (
    <Card>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">
            Vendor {session.vendor_id.slice(0, 8)} - Round {session.current_round}
          </h3>
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
            Active
          </span>
        </div>

        <div className="space-y-3">
          {latestMessages.map((message, idx) => (
            <div key={idx} className={message.actor === 'buyer' ? 'pl-4 border-l-2 border-blue-500' : 'pl-4 border-l-2 border-gray-300'}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-xs font-medium text-gray-600 mb-1">
                    {message.actor === 'buyer' ? 'Our Agent' : 'Vendor Response'}
                  </p>
                  <p className="text-sm text-gray-900">
                    ${message.proposal.unit_price}/seat • {message.proposal.term_months}mo term • {message.proposal.payment_terms}
                  </p>
                  {message.justification_bullets.length > 0 && (
                    <ul className="mt-2 text-xs text-gray-600 space-y-1">
                      {message.justification_bullets.map((bullet, bidx) => (
                        <li key={bidx}>• {bullet}</li>
                      ))}
                    </ul>
                  )}
                </div>
                <AIExplainer
                  title="this move"
                  reasoning={[
                    { label: 'Strategy', value: message.machine_rationale.concession_taken },
                    { label: 'Price Delta', value: `$${message.proposal.unit_price}` },
                    ...Object.entries(message.machine_rationale.score_components).map(([k, v]) => ({
                      label: k,
                      value: v.toFixed(2),
                    })),
                  ]}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-600">
            Next step: <span className="font-medium text-gray-900">{latestMessages[0]?.next_step_hint || 'Waiting for response...'}</span>
          </p>
        </div>
      </div>
    </Card>
  )
}
