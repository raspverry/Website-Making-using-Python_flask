export interface User {
  id: number;
  email: string;
  name: string;
  plan: 'free' | 'starter' | 'pro' | 'agency';
}

export interface Site {
  id: number;
  uid: string;
  url: string;
  name: string;
  compliance_score: number | null;
  last_scan_at: string | null;
}

export interface Scan {
  id: number;
  uid: string;
  site_id: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  score: number | null;
  pages_scanned: number;
  total_violations: number;
  critical_count: number;
  serious_count: number;
  moderate_count: number;
  minor_count: number;
  created_at: string;
  completed_at: string | null;
}

export interface Violation {
  id: number;
  rule_id: string;
  rule_name: string;
  severity: 'critical' | 'serious' | 'moderate' | 'minor';
  wcag_criteria: string;
  description: string;
  element_html: string;
  page_url: string;
  fix_suggestion: string;
  selector: string;
}
