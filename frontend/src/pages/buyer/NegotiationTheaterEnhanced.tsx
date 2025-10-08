import { useState, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Heading,
  Text,
  SimpleGrid,
  VStack,
  HStack,
  Button,
  useDisclosure,
} from '@chakra-ui/react'
import { ArrowLeft, FileText, Play } from 'lucide-react'
import { api } from '../../services/api'
import { VendorOfferCard } from '../../components/buyer/negotiation/VendorOfferCard'
import { NegotiationSummaryHeader } from '../../components/buyer/negotiation/NegotiationSummaryHeader'
import { AIReasoningPanel } from '../../components/buyer/negotiation/AIReasoningPanel'
import { NegotiationRoundsTimeline } from '../../components/buyer/negotiation/NegotiationRoundsTimeline'
import { EnhancedInterventionPanel } from '../../components/buyer/negotiation/EnhancedInterventionPanel'
import { CommunicationFeed, type Message } from '../../components/buyer/negotiation/CommunicationFeed'
import { AuditLogModal, type AuditEntry } from '../../components/buyer/negotiation/AuditLogModal'
import { OfferDetailsPanel } from '../../components/buyer/negotiation/OfferDetailsPanel'

export function NegotiationTheaterEnhanced(): JSX.Element {
  const { requestId } = useParams<{ requestId: string }>()
  const navigate = useNavigate()
  const { open: isAuditOpen, onOpen: openAudit, onClose: closeAudit } = useDisclosure()
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'details' | 'reasoning' | 'rounds' | 'communication'>('details')

  // Fetch request data
  const { data: request } = useQuery({
    queryKey: ['request', requestId],
    queryFn: async () => {
      if (!requestId) throw new Error('No request ID')
      return await api.getRequest(requestId)
    },
    enabled: Boolean(requestId),
  })

  // Fetch negotiations
  const { data: sessions, isLoading } = useQuery({
    queryKey: ['negotiations', requestId],
    queryFn: async () => {
      if (!requestId) return []
      return await api.getNegotiationsForRequest(requestId)
    },
    enabled: Boolean(requestId),
  })

  const activeSessions = useMemo(
    () => (sessions ?? []).filter((s) => s.status === 'active'),
    [sessions]
  )

  const selectedSession = useMemo(
    () => activeSessions.find((s) => s.session_id === selectedSessionId) || activeSessions[0],
    [activeSessions, selectedSessionId]
  )

  // Fetch negotiation events for the selected session
  const { data: events } = useQuery({
    queryKey: ['negotiation-events', selectedSession?.session_id],
    queryFn: async () => {
      if (!selectedSession?.session_id) return []
      return await api.getNegotiationEvents(selectedSession.session_id)
    },
    enabled: Boolean(selectedSession?.session_id),
  })

  // Calculate metrics
  const bestOffer = useMemo(() => {
    if (!activeSessions.length) return null
    return activeSessions.reduce((best, current) =>
      (current.current_price || Infinity) < (best.current_price || Infinity) ? current : best
    )
  }, [activeSessions])

  const projectedSavings = useMemo(() => {
    if (!bestOffer?.current_price || !request?.budget_max) return 0
    return Math.max(0, request.budget_max - bestOffer.current_price)
  }, [bestOffer, request])

  // Transform events into audit entries
  const auditEntries = useMemo((): AuditEntry[] => {
    if (!events || events.length === 0) {
      // Fallback to mock data if no events
      return [
        {
          id: '1',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          actor: 'agent',
          action: 'Negotiation Started',
          details: `Buyer agent initiated negotiation with ${selectedSession?.vendor_name || 'vendor'}`,
          level: 'info',
          metadata: { vendor: selectedSession?.vendor_name },
        },
      ]
    }

    return events.map((event) => ({
      id: event.id,
      timestamp: event.timestamp,
      actor: event.event_type.includes('buyer') ? 'agent' : event.event_type.includes('policy') ? 'policy' : 'system',
      action: event.event_type.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
      details: event.event_data?.message || JSON.stringify(event.event_data),
      level: event.event_type.includes('error') ? 'error' : event.event_type.includes('success') ? 'success' : 'info',
      metadata: event.event_data,
    }))
  }, [events, selectedSession])

  // Mock data for demo
  const mockMessages: Message[] = [
    {
      id: '1',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      sender: 'agent',
      senderName: 'Procurement Agent',
      content: 'Initiated negotiations with 3 vendors based on your requirements.',
      type: 'system',
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 1800000).toISOString(),
      sender: 'vendor',
      senderName: 'OrbitCRM',
      content: 'We can offer $950/month for 200 users with annual contract.',
      type: 'message',
    },
    {
      id: '3',
      timestamp: new Date(Date.now() - 900000).toISOString(),
      sender: 'agent',
      senderName: 'Procurement Agent',
      content: 'Counter-offered at $900/month. Vendor is considering.',
      type: 'system',
    },
  ]

  // TODO: Replace with real communication messages from backend
  // For now, using audit events as communication feed

  const mockReasoning = {
    summary: `Best budget fit with strong feature coverage. OrbitCRM offers the most competitive pricing at $${bestOffer?.current_price?.toLocaleString() || '950'}/month while meeting 90% of must-have requirements.`,
    factors: [
      {
        category: 'budget' as const,
        weight: 0.4,
        description: `$${projectedSavings.toLocaleString()} under budget ceiling`,
        score: 0.92,
      },
      {
        category: 'features' as const,
        weight: 0.3,
        description: '18 of 20 must-haves met, including API access and SSO',
        score: 0.90,
      },
      {
        category: 'compliance' as const,
        weight: 0.2,
        description: 'SOC 2, GDPR, and data residency requirements satisfied',
        score: 1.0,
      },
      {
        category: 'risk' as const,
        weight: 0.1,
        description: 'Low-risk vendor with 95% customer satisfaction',
        score: 0.95,
      },
    ],
    recommendation: 'Accept this offer. Price is highly competitive, critical requirements are met, and vendor has strong compliance posture. Recommend proceeding to contract phase.',
  }

  if (isLoading) {
    return (
      <Box py={12} textAlign="center">
        <Text>Loading negotiation theater...</Text>
      </Box>
    )
  }

  return (
    <Box maxW="1400px" mx="auto" px={{ base: 4, lg: 6 }} py={6}>
      {/* Back Button */}
      <Button
        variant="ghost"
        size="sm"
        leftIcon={<ArrowLeft className="h-4 w-4" />}
        onClick={() => navigate('/dashboard')}
        mb={4}
      >
        Back to Dashboard
      </Button>

      <VStack align="stretch" gap={6}>
        {/* Summary Header */}
        <NegotiationSummaryHeader
          requestName={request?.description || 'Loading...'}
          totalVendors={sessions?.length || 0}
          activeNegotiations={activeSessions.length}
          projectedSavings={projectedSavings}
          timeShortened={18}
          complianceWins={3}
          bestOfferPrice={bestOffer?.current_price}
          targetBudget={request?.budget_max}
        />

        {/* Main Content: Split Layout */}
        <SimpleGrid columns={{ base: 1, xl: 3 }} gap={6}>
          {/* Left: Vendor Offers (2/3 width on xl) */}
          <Box gridColumn={{ xl: 'span 2' }}>
            <VStack align="stretch" gap={6}>
              {/* Vendor Cards */}
              <Box>
                <Heading size="md" mb={4} color="var(--core-color-text-primary)">
                  Active Negotiations
                </Heading>
                <SimpleGrid columns={{ base: 1, md: 2 }} gap={4}>
                  {activeSessions.map((session, index) => (
                    <VendorOfferCard
                      key={session.session_id}
                      session={session}
                      rank={index + 1}
                      budgetMax={request?.budget_max}
                      mustHaves={request?.must_haves}
                      onClick={() => setSelectedSessionId(session.session_id)}
                      onAccept={() => {
                        alert(`Accepting offer from ${session.vendor_name}`)
                      }}
                      onIntervene={() => {
                        alert('Opening intervention panel')
                      }}
                    />
                  ))}
                </SimpleGrid>
              </Box>

              {/* Tabbed Details */}
              {selectedSession && (
                <Box>
                  {/* Tab List */}
                  <HStack
                    gap={0}
                    borderBottomWidth="1px"
                    borderColor="var(--core-color-border-default)"
                  >
                    {[
                      { id: 'details', label: 'Offer Details' },
                      { id: 'reasoning', label: 'AI Reasoning' },
                      { id: 'rounds', label: 'Round History' },
                      { id: 'communication', label: 'Communication' },
                    ].map((tab) => (
                      <Button
                        key={tab.id}
                        variant="ghost"
                        size="md"
                        borderRadius="0"
                        borderBottomWidth="2px"
                        borderBottomColor={
                          activeTab === tab.id
                            ? 'var(--core-color-brand-primary)'
                            : 'transparent'
                        }
                        color={
                          activeTab === tab.id
                            ? 'var(--core-color-brand-primary)'
                            : 'var(--core-color-text-secondary)'
                        }
                        fontWeight={activeTab === tab.id ? 'semibold' : 'normal'}
                        onClick={() => setActiveTab(tab.id as any)}
                        _hover={{
                          bg: 'var(--core-color-surface-subtle)',
                        }}
                      >
                        {tab.label}
                      </Button>
                    ))}
                  </HStack>

                  {/* Tab Panels */}
                  <Box pt={4}>
                    {activeTab === 'details' && (
                      <OfferDetailsPanel
                        session={selectedSession}
                        requestBudget={{ min: request?.budget_min, max: request?.budget_max }}
                        mustHaves={request?.must_haves}
                      />
                    )}

                    {activeTab === 'reasoning' && (
                      <AIReasoningPanel reasoning={mockReasoning} />
                    )}

                    {activeTab === 'rounds' && (
                      <NegotiationRoundsTimeline
                        rounds={[
                          {
                            round: 1,
                            timestamp: new Date(Date.now() - 7200000).toISOString(),
                            actor: 'seller',
                            price: 1050,
                            strategy: 'Initial',
                            rationale: ['Starting at list price', 'Annual contract discount applied'],
                          },
                          {
                            round: 2,
                            timestamp: new Date(Date.now() - 5400000).toISOString(),
                            actor: 'buyer',
                            price: 900,
                            strategy: 'Competitive',
                            rationale: ['Counter-offered based on budget', 'Requested additional features'],
                          },
                          {
                            round: 3,
                            timestamp: new Date(Date.now() - 3600000).toISOString(),
                            actor: 'seller',
                            price: selectedSession.current_price || 950,
                            strategy: 'Collaborative',
                            accepted: false,
                            rationale: ['Split the difference', 'Added premium support at no cost'],
                          },
                        ]}
                      />
                    )}

                    {activeTab === 'communication' && (
                      <CommunicationFeed
                        messages={mockMessages}
                        onSendMessage={(msg) => console.log('Send:', msg)}
                        onTagApprover={() => alert('Tagging approver')}
                        onTagLegal={() => alert('Tagging legal')}
                      />
                    )}
                  </Box>
                </Box>
              )}
            </VStack>
          </Box>

          {/* Right: Controls & Actions (1/3 width on xl) */}
          <VStack align="stretch" gap={4}>
            {/* Intervention Panel */}
            <EnhancedInterventionPanel
              currentBudget={{ min: request?.budget_min, max: request?.budget_max }}
              onAdjustBudget={(newBudget) => {
                console.log('Adjust budget:', newBudget)
              }}
              onAddRequirement={(req) => {
                console.log('Add requirement:', req)
              }}
              onPauseNegotiations={() => {
                console.log('Pause negotiations')
              }}
              onAcceptOffer={(sessionId) => {
                console.log('Accept offer:', sessionId)
              }}
              canAccept={Boolean(bestOffer)}
              bestSessionId={bestOffer?.session_id}
            />

            {/* Audit Log Button */}
            <Button
              variant="outline"
              leftIcon={<FileText className="h-4 w-4" />}
              onClick={openAudit}
              w="full"
            >
              View Complete Audit Trail
            </Button>

            {/* Quick Actions */}
            <Box
              p={4}
              borderWidth="1px"
              borderColor="var(--core-color-border-default)"
              borderRadius="lg"
              bg="var(--core-color-surface-canvas)"
            >
              <Text fontSize="sm" fontWeight="semibold" mb={3} color="var(--core-color-text-primary)">
                Quick Actions
              </Text>
              <VStack align="stretch" gap={2}>
                <Button
                  size="sm"
                  variant="ghost"
                  justifyContent="start"
                  leftIcon={<Play className="h-4 w-4" />}
                  onClick={() => alert('Re-running auto-negotiate')}
                >
                  Re-run Auto-Negotiate
                </Button>
              </VStack>
            </Box>
          </VStack>
        </SimpleGrid>
      </VStack>

      {/* Audit Log Modal */}
      <AuditLogModal
        isOpen={isAuditOpen}
        onClose={closeAudit}
        sessionId={selectedSession?.session_id || 'unknown'}
        entries={auditEntries}
      />
    </Box>
  )
}
