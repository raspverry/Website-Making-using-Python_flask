import { config } from './config';

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = config.apiUrl;
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
    if (!res.ok) {
      throw new Error(`API error: ${res.status}`);
    }
    return res.json();
  }

  // Sites
  getSites() { return this.request<any[]>('/api/v1/sites'); }
  getSite(uid: string) { return this.request<any>(`/api/v1/sites/${uid}`); }
  createSite(url: string, name: string) {
    return this.request<any>('/api/v1/sites', { method: 'POST', body: JSON.stringify({ url, name }) });
  }

  // Scans
  startScan(siteUid: string) {
    return this.request<any>(`/api/v1/sites/${siteUid}/scan`, { method: 'POST' });
  }
  getScan(scanUid: string) { return this.request<any>(`/api/v1/scans/${scanUid}`); }

  // Agent
  askAgent(siteUid: string, question: string) {
    return this.request<{ answer: string }>(`/api/v1/sites/${siteUid}/agent/ask`, {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
  }
}

export const api = new ApiClient();
