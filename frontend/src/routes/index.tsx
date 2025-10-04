import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Outlet,
} from 'react-router-dom'
import { AppLayout } from '../components/layout/AppLayout'
import { useAuthStore } from '../store/auth'
import { Login } from '../pages/auth/Login'
import { BuyerDashboard } from '../pages/buyer/Dashboard'
import { NewRequest } from '../pages/buyer/NewRequest'
import { NegotiationTheater } from '../pages/buyer/NegotiationTheater'
import { VendorNegotiationView } from '../pages/buyer/VendorNegotiationView'
import { ApprovalWorkspace } from '../pages/buyer/ApprovalWorkspace'
import { Portfolio } from '../pages/buyer/Portfolio'
import { SellerDashboard } from '../pages/seller/SellerDashboard'
import { SellerNegotiations } from '../pages/seller/SellerNegotiations'
import { SellerGuardrails } from '../pages/seller/SellerGuardrails'
import { SellerIntelligence } from '../pages/seller/SellerIntelligence'
import { SellerTerritory } from '../pages/seller/SellerTerritory'

function ProtectedApp(): JSX.Element {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return (
    <AppLayout>
      <Outlet />
    </AppLayout>
  )
}

export function AppRoutes(): JSX.Element {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedApp />}>
          <Route index element={<BuyerDashboard />} />
          <Route path="requests">
            <Route path="new" element={<NewRequest />} />
            <Route
              path=":requestId/negotiate"
              element={<NegotiationTheater />}
            />
          </Route>
          <Route path="negotiations">
            <Route path=":requestId" element={<NegotiationTheater />} />
            <Route path=":requestId/:sessionId" element={<VendorNegotiationView />} />
          </Route>
          <Route path="approvals" element={<ApprovalWorkspace />} />
          <Route path="portfolio" element={<Portfolio />} />

          <Route path="seller">
            <Route index element={<SellerDashboard />} />
            <Route path="negotiations" element={<SellerNegotiations />} />
            <Route path="guardrails" element={<SellerGuardrails />} />
            <Route path="intelligence" element={<SellerIntelligence />} />
            <Route path="territory" element={<SellerTerritory />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
