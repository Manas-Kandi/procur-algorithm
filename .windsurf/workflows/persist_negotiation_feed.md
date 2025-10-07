---
description: Persist negotiation live feed
---

1. Modify the backend to store live feed events in the database.
   - Update the `StreamingNegotiationWrapper` to save each event to a `NegotiationEvent` table.
   - Ensure each event includes a timestamp, session ID, event type, and event data.

2. Update the frontend to keep the live feed visible.
   - Modify the frontend component to keep the live feed open after the negotiation completes.
   - Provide a "Save Feed" button to store the feed locally or in the cloud.

3. Implement a retrieval mechanism for past live feeds.
   - Create an API endpoint to fetch past negotiation events by session ID.
   - Display past events in the frontend when requested.

4. Test the workflow end-to-end.
   - Start a negotiation and verify that the live feed persists and is stored correctly.
   - Retrieve and display past feeds to ensure data integrity.
