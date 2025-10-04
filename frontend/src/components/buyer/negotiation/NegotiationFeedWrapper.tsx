import { useNegotiationStream } from '../../../hooks/useNegotiationStream'
import { LiveNegotiationFeed } from './LiveNegotiationFeed'
import { NegotiationFeed } from './NegotiationFeed'
import type { NegotiationSession } from '../../../types'

interface NegotiationFeedWrapperProps {
  session: NegotiationSession
}

export function NegotiationFeedWrapper({ session }: NegotiationFeedWrapperProps): JSX.Element {
  // This hook is now called at the component level, not inside a map
  const streamHook = useNegotiationStream(session.session_id)

  return streamHook.events.length > 0 ? (
    <LiveNegotiationFeed
      events={streamHook.events}
      vendorName={session.vendor_name || 'Unknown Vendor'}
    />
  ) : (
    <NegotiationFeed session={session} />
  )
}
