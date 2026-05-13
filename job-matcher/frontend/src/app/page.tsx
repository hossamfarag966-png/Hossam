'use client';

import { useState, useEffect } from 'react';
import { fetchStats, fetchJobs, triggerFetchJobs, triggerDigest, DashboardStats, Job } from '@/lib/api';
import { JobCard } from '@/components/JobCard';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [topJobs, setTopJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionStatus, setActionStatus] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [statsData, jobsData] = await Promise.all([
        fetchStats(),
        fetchJobs({ sort_by: 'match_score', limit: 5, status: 'new' }),
      ]);
      setStats(statsData);
      setTopJobs(jobsData.jobs);
    } catch (e) {
      console.error('Failed to load dashboard data:', e);
    } finally {
      setLoading(false);
    }
  }

  async function handleFetchJobs() {
    setActionStatus('Fetching jobs...');
    try {
      await triggerFetchJobs();
      setActionStatus('Job fetch triggered! Results will appear shortly.');
      setTimeout(() => { setActionStatus(''); loadData(); }, 5000);
    } catch (e) {
      setActionStatus('Failed to trigger job fetch');
    }
  }

  async function handleSendDigest() {
    setActionStatus('Sending digest...');
    try {
      await triggerDigest();
      setActionStatus('Digest sent!');
      setTimeout(() => setActionStatus(''), 3000);
    } catch (e) {
      setActionStatus('Failed to send digest');
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-gray-600 mt-1">Your daily career intelligence overview</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleFetchJobs}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition"
          >
            Fetch New Jobs
          </button>
          <button
            onClick={handleSendDigest}
            className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition"
          >
            Send Digest Now
          </button>
        </div>
      </div>

      {actionStatus && (
        <div className="bg-blue-50 text-blue-700 px-4 py-3 rounded-lg text-sm">
          {actionStatus}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard label="Total Jobs" value={stats?.total_jobs || 0} icon="&#128203;" />
        <StatCard label="New Matches" value={stats?.new_jobs || 0} icon="&#10024;" color="green" />
        <StatCard label="Applied" value={stats?.applied_jobs || 0} icon="&#128232;" color="blue" />
        <StatCard label="Avg Match" value={`${stats?.avg_match_score || 0}%`} icon="&#127919;" color="purple" />
      </div>

      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Top Matches</h3>
          <a href="/jobs" className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            View all &rarr;
          </a>
        </div>
        {topJobs.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-gray-200">
            <p className="text-gray-500 text-lg">No jobs yet.</p>
            <p className="text-gray-400 mt-2">Upload your CV in Settings, then click &quot;Fetch New Jobs&quot; to get started.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {topJobs.map((job) => (
              <JobCard key={job.id} job={job} onStatusChange={loadData} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, color = 'gray' }: { label: string; value: string | number; icon: string; color?: string }) {
  const colorMap: Record<string, string> = {
    gray: 'bg-gray-50 border-gray-200',
    green: 'bg-green-50 border-green-200',
    blue: 'bg-blue-50 border-blue-200',
    purple: 'bg-purple-50 border-purple-200',
  };

  return (
    <div className={`rounded-xl p-5 border ${colorMap[color] || colorMap.gray}`}>
      <div className="flex items-center justify-between">
        <span className="text-2xl" dangerouslySetInnerHTML={{ __html: icon }}></span>
      </div>
      <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
      <p className="text-sm text-gray-600 mt-1">{label}</p>
    </div>
  );
}
