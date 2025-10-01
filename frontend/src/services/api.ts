import axios, { AxiosInstance, AxiosError } from 'axios'
import type { Request, Vendor, Offer, NegotiationSession, Contract, User, DashboardMetrics } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', { username: email, password })
    return response.data
  }

  async register(email: string, password: string, username: string, role: string) {
    const response = await this.client.post('/auth/register', { email, password, username, role })
    return response.data
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/auth/me')
    return response.data
  }

  // Request endpoints
  async createRequest(data: Partial<Request>): Promise<Request> {
    const response = await this.client.post('/requests', data)
    return response.data
  }

  async getRequests(status?: string): Promise<Request[]> {
    const response = await this.client.get('/requests', { params: { status } })
    return response.data
  }

  async getRequest(requestId: string): Promise<Request> {
    const response = await this.client.get(`/requests/${requestId}`)
    return response.data
  }

  async updateRequest(requestId: string, data: Partial<Request>): Promise<Request> {
    const response = await this.client.patch(`/requests/${requestId}`, data)
    return response.data
  }

  // Vendor endpoints
  async getVendors(search?: string): Promise<Vendor[]> {
    const response = await this.client.get('/vendors', { params: { search } })
    return response.data
  }

  async getVendor(vendorId: string): Promise<Vendor> {
    const response = await this.client.get(`/vendors/${vendorId}`)
    return response.data
  }

  async searchVendors(query: string, filters?: Record<string, any>): Promise<Vendor[]> {
    const response = await this.client.post('/vendors/search', { query, ...filters })
    return response.data
  }

  // Negotiation endpoints
  async startNegotiation(requestId: string, vendorIds: string[]): Promise<NegotiationSession[]> {
    const response = await this.client.post(`/negotiations/start`, { request_id: requestId, vendor_ids: vendorIds })
    return response.data
  }

  async getNegotiation(sessionId: string): Promise<NegotiationSession> {
    const response = await this.client.get(`/negotiations/${sessionId}`)
    return response.data
  }

  async getNegotiationsForRequest(requestId: string): Promise<NegotiationSession[]> {
    const response = await this.client.get(`/negotiations/request/${requestId}`)
    return response.data
  }

  async submitOffer(sessionId: string, offer: Partial<Offer>): Promise<NegotiationSession> {
    const response = await this.client.post(`/negotiations/${sessionId}/offer`, offer)
    return response.data
  }

  async acceptOffer(sessionId: string, offerId: string): Promise<NegotiationSession> {
    const response = await this.client.post(`/negotiations/${sessionId}/accept`, { offer_id: offerId })
    return response.data
  }

  // Contract endpoints
  async getContract(contractId: string): Promise<Contract> {
    const response = await this.client.get(`/contracts/${contractId}`)
    return response.data
  }

  async generateContract(requestId: string, offerId: string): Promise<Contract> {
    const response = await this.client.post(`/contracts/generate`, { request_id: requestId, offer_id: offerId })
    return response.data
  }

  async approveContract(contractId: string): Promise<Contract> {
    const response = await this.client.post(`/contracts/${contractId}/approve`)
    return response.data
  }

  async signContract(contractId: string): Promise<Contract> {
    const response = await this.client.post(`/contracts/${contractId}/sign`)
    return response.data
  }

  // Dashboard endpoints
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await this.client.get('/dashboard/metrics')
    return response.data
  }

  async getUpcomingRenewals(daysAhead: number = 60): Promise<any[]> {
    const response = await this.client.get('/dashboard/renewals', { params: { days_ahead: daysAhead } })
    return response.data
  }

  async getPendingApprovals(): Promise<any[]> {
    const response = await this.client.get('/dashboard/approvals')
    return response.data
  }
}

export const api = new ApiClient()
