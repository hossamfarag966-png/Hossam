'use client';

import { useState, useEffect } from 'react';
import { fetchJobs, Job, JobListResponse } from '@/lib/api';
import { JobCard } from '@/components/JobCard';

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [offset, setOffset] = useState(0);
  const limit = 20;

  const [status, setStatus] = useState<string>('');
  const [source, setSource] = useState<string>('');
  const [minMatch, setMinMatch] = useState<number>(0);
  const [sortBy, setSortBy] = useState<string>('match_score');

  useEffect(() => {
    loadJobs();
  }, [status, source, minMatch, sortBy, offset]);

  async function loadJobs() {
    setLoading(true);
    try {
      const data = await fetchJobs({
        status: status || undefined,
        source: source || undefined,
        min_match: minMatch || undefined,
        sort_by: sortBy,
        limit,
        offset,
      });
      setJobs(data.jobs);
      setTotal(data.total);
    } catch (e) {
      console.error('Failed to load jobs:', e);
    } finally {
      setLoading(false);
    }
  }

  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">All Jobs</h2>
        <p className="text-gray-600 mt-1">{total} jobs found</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase">Status</label>
            <select
              value={status}
              onChange={(e) => { setStatus(e.target.value); setOffset(0); }}
              className="mt-1 w-full rounded-lg border-gray-300 bg-gray-50 text-sm p-2 border"
            >
              <option value="">All</option>
              <option value="new">New</option>
              <option value="interested">Interested</option>
              <option value="applied">Applied</option>
              <option value="rejected">Rejected</option>
              <option value="not_relevant">Not Relevant</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase">Source</label>
            <select
              value={source}
              onChange={(e) => { setSource(e.target.value); setOffset(0); }}
              className="mt-1 w-full rounded-lg border-gray-300 bg-gray-50 text-sm p-2 border"
            >
              <option value="">All Sources</option>
              <option value="remoteok">RemoteOK</option>
              <option value="remotive">Remotive</option>
              <option value="weworkremotely">We Work Remotely</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase">Min Match %</label>
            <input
              type="number"
              min={0}
              max={100}
              value={minMatch}
              onChange={(e) => { setMinMatch(Number(e.target.value)); setOffset(0); }}
              className="mt-1 w-full rounded-lg border-gray-300 bg-gray-50 text-sm p-2 border"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => { setSortBy(e.target.value); setOffset(0); }}
              className="mt-1 w-full rounded-lg border-gray-300 bg-gray-50 text-sm p-2 border"
            >
              <option value="match_score">Match Score</option>
              <option value="posted_at">Date Posted</option>
              <option value="acceptance_likelihood">Acceptance Likelihood</option>
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : jobs.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center border border-gray-200">
          <p className="text-gray-500 text-lg">No jobs match your filters.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} onStatusChange={loadJobs} />
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-4">
          <button
            disabled={currentPage <= 1}
            onClick={() => setOffset(Math.max(0, offset - limit))}
            className="px-4 py-2 rounded-lg bg-white border border-gray-300 text-sm disabled:opacity-50 hover:bg-gray-50"
          >
            Previous
          </button>
          <span className="text-sm text-gray-600">
            Page {currentPage} of {totalPages}
          </span>
          <button
            disabled={currentPage >= totalPages}
            onClick={() => setOffset(offset + limit)}
            className="px-4 py-2 rounded-lg bg-white border border-gray-300 text-sm disabled:opacity-50 hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
