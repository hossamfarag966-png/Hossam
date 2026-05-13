const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Job {
  id: string;
  external_id?: string;
  source: string;
  title: string;
  company: string;
  company_logo?: string;
  location?: string;
  work_mode?: string;
  url: string;
  seniority?: string;
  skills_required?: string[];
  skills_nice_to_have?: string[];
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  match_score?: number;
  match_explanation?: string;
  skill_coverage?: number;
  semantic_score?: number;
  estimated_salary_low?: number;
  estimated_salary_mid?: number;
  estimated_salary_high?: number;
  estimated_salary_currency?: string;
  acceptance_likelihood?: number;
  acceptance_factors?: { positive: string[]; negative: string[] };
  status: string;
  user_notes?: string;
  posted_at?: string;
  fetched_at?: string;
  tags?: string[];
}

export interface JobListResponse {
  jobs: Job[];
  total: number;
  limit: number;
  offset: number;
}

export interface Profile {
  id: string;
  name?: string;
  email?: string;
  headline?: string;
  summary?: string;
  location?: string;
  skills?: any;
  experience?: any;
  education?: any;
  target_roles?: any;
  target_locations?: any;
  work_mode?: string;
  min_salary?: number;
  salary_currency?: string;
  years_experience?: number;
  cv_filename?: string;
  linkedin_export_filename?: string;
}

export interface DashboardStats {
  total_jobs: number;
  new_jobs: number;
  applied_jobs: number;
  interested_jobs: number;
  avg_match_score: number;
}

export async function fetchJobs(params?: {
  status?: string;
  source?: string;
  min_match?: number;
  sort_by?: string;
  limit?: number;
  offset?: number;
}): Promise<JobListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set('status', params.status);
  if (params?.source) searchParams.set('source', params.source);
  if (params?.min_match) searchParams.set('min_match', params.min_match.toString());
  if (params?.sort_by) searchParams.set('sort_by', params.sort_by);
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());

  const res = await fetch(`${API_URL}/api/jobs?${searchParams.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch jobs');
  return res.json();
}

export async function updateJobStatus(jobId: string, status: string, notes?: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/jobs/${jobId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, notes }),
  });
  if (!res.ok) throw new Error('Failed to update job status');
}

export async function fetchProfile(): Promise<Profile> {
  const res = await fetch(`${API_URL}/api/profile`);
  if (!res.ok) throw new Error('Failed to fetch profile');
  return res.json();
}

export async function uploadCV(file: File): Promise<Profile> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_URL}/api/profile/cv`, { method: 'POST', body: formData });
  if (!res.ok) throw new Error('Failed to upload CV');
  return res.json();
}

export async function uploadLinkedInExport(file: File): Promise<Profile> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_URL}/api/profile/linkedin`, { method: 'POST', body: formData });
  if (!res.ok) throw new Error('Failed to upload LinkedIn export');
  return res.json();
}

export async function updatePreferences(prefs: any): Promise<Profile> {
  const res = await fetch(`${API_URL}/api/profile/preferences`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(prefs),
  });
  if (!res.ok) throw new Error('Failed to update preferences');
  return res.json();
}

export async function fetchStats(): Promise<DashboardStats> {
  const res = await fetch(`${API_URL}/api/stats`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function triggerFetchJobs(): Promise<void> {
  const res = await fetch(`${API_URL}/api/fetch-jobs`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to trigger job fetch');
}

export async function triggerDigest(): Promise<void> {
  const res = await fetch(`${API_URL}/api/send-digest`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to trigger digest');
}
