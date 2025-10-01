import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import { Navigation } from '../components/layout/Navigation'
import { Login } from '../pages/auth/Login'
import { BuyerDashboard } from '../pages/buyer/Dashboard'
import { NewRequest } from '../pages/buyer/NewRequest'
import { NegotiationTheater } from '../pages/buyer/NegotiationTheater'
import { ApprovalWorkspace } from '../pages/buyer/ApprovalWorkspace'
import { Portfolio } from '../pages/buyer/Portfolio'
import { SellerDashboard } from '../pages/seller/SellerDashboard'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function AuthenticatedLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50">
      <Navigation />
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  )
}

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth Routes */}
        <Route path="/login" element={<Login />} />
        
        {/* Buyer Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <BuyerDashboard />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/requests/new"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <NewRequest />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/requests/:requestId/negotiate"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <NegotiationTheater />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/approvals"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <ApprovalWorkspace />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/portfolio"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <Portfolio />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        
        {/* Seller Routes */}
        <Route
          path="/seller"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <SellerDashboard />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        
        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
