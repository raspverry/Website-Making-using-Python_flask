import { config } from './config';
import type { Site, Scan, Violation } from '@/types';

export interface ScanResult {
  scan: Scan;
  violations: Violation[];
}

export interface ApiError {
  detail: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = config.apiUrl;
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options?.headers as Record<string, string>),
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    const res = await fetch(`${this.baseUrl}${path}`, { ...options, headers });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(error.detail || `API error: ${res.status}`);
    }
    return res.json();
  }

  // Auth
  async signup(email: string, password: string, name: string) {
    return this.request<{ access_token: string; user: { id: number; email: string; name: string; plan: string } }>('/api/v1/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });
  }

  async login(email: string, password: string) {
    return this.request<{ access_token: string; user: { id: number; email: string; name: string; plan: string } }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  // Sites
  getSites() { return this.request<Site[]>('/api/v1/sites'); }
  getSite(uid: string) { return this.request<Site>(`/api/v1/sites/${uid}`); }
  createSite(url: string, name: string) {
    return this.request<Site>('/api/v1/sites', { method: 'POST', body: JSON.stringify({ url, name }) });
  }

  deleteSite(uid: string) {
    return this.request<{ message: string }>(`/api/v1/sites/${uid}`, { method: 'DELETE' });
  }

  // Scans
  startScan(siteUid: string) {
    return this.request<ScanResult>(`/api/v1/sites/${siteUid}/scan`, { method: 'POST' });
  }
  getLatestScan(siteUid: string) {
    return this.request<ScanResult>(`/api/v1/sites/${siteUid}/latest-scan`);
  }

  // Agent
  askAgent(siteUid: string, question: string) {
    return this.request<{ answer: string }>(`/api/v1/sites/${siteUid}/agent/ask`, {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
  }

  getSummary(siteUid: string) {
    return this.request<{ summary: string; score: number; total_violations: number }>(`/api/v1/sites/${siteUid}/agent/summary`);
  }

  // Billing
  createCheckout(plan: string) {
    return this.request<{ checkout_url: string; session_id: string }>(`/api/v1/billing/checkout?plan=${encodeURIComponent(plan)}`, {
      method: 'POST',
    });
  }

  createPortal() {
    return this.request<{ portal_url: string }>('/api/v1/billing/portal', { method: 'POST' });
  }

  getSubscription() {
    return this.request<{ plan: string; status: string; current_period_end: string | null }>('/api/v1/billing/subscription');
  }
}

export const api = new ApiClient();
