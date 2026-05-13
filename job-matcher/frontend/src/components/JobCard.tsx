'use client';

import { useState } from 'react';
import { Job, updateJobStatus } from '@/lib/api';

interface JobCardProps {
  job: Job;
  onStatusChange?: () => void;
  expanded?: boolean;
}

export function JobCard({ job, onStatusChange, expanded = false }: JobCardProps) {
  const [showDetails, setShowDetails] = useState(expanded);
  const [updating, setUpdating] = useState(false);

  async function handleStatus(status: string) {
    setUpdating(true);
    try {
      await updateJobStatus(job.id, status);
      onStatusChange?.();
    } catch (e) {
      console.error('Failed to update status:', e);
    } finally {
      setUpdating(false);
    }
  }

  const matchColor = (job.match_score || 0) >= 70
    ? 'text-green-700 bg-green-100'
    : (job.match_score || 0) >= 40
      ? 'text-yellow-700 bg-yellow-100'
      : 'text-gray-700 bg-gray-100';

  const acceptanceColor = (job.acceptance_likelihood || 0) >= 60
    ? 'text-green-700 bg-green-100'
    : (job.acceptance_likelihood || 0) >= 35
      ? 'text-yellow-700 bg-yellow-100'
      : 'text-red-700 bg-red-100';

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h4 className="text-lg font-semibold text-gray-900">{job.title}</h4>
            <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded">{job.source}</span>
          </div>
          <p className="text-sm text-gray-600 mt-1">
            {job.company}
            {job.location && <span> &bull; {job.location}</span>}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${matchColor}`}>
            {job.match_score?.toFixed(0) || '?'}% match
          </span>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mt-3">
        {job.estimated_salary_mid && (
          <span className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium">
            ~${Math.round(job.estimated_salary_mid / 1000)}k/yr
          </span>
        )}
        {job.acceptance_likelihood && (
          <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${acceptanceColor}`}>
            {job.acceptance_likelihood.toFixed(0)}% acceptance
          </span>
        )}
        {job.work_mode && (
          <span className="px-2.5 py-1 bg-purple-50 text-purple-700 rounded-full text-xs font-medium">
            {job.work_mode}
          </span>
        )}
        {job.seniority && (
          <span className="px-2.5 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
            {job.seniority}
          </span>
        )}
      </div>

      {job.match_explanation && (
        <p className="text-sm text-gray-500 italic mt-3">{job.match_explanation}</p>
      )}

      {showDetails && (
        <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
          {job.skills_required && Array.isArray(job.skills_required) && job.skills_required.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase mb-1">Required Skills</p>
              <div className="flex flex-wrap gap-1">
                {job.skills_required.map((skill, i) => (
                  <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs">{skill}</span>
                ))}
              </div>
            </div>
          )}

          {job.estimated_salary_low && (
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase mb-1">Estimated Salary Range</p>
              <p className="text-sm text-gray-700">
                ${job.estimated_salary_low.toLocaleString()} &mdash; ${job.estimated_salary_mid?.toLocaleString()} &mdash; ${job.estimated_salary_high?.toLocaleString()} ({job.estimated_salary_currency || 'USD'})
              </p>
            </div>
          )}

          {job.acceptance_factors && (
            <div className="grid grid-cols-2 gap-4">
              {job.acceptance_factors.positive?.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-green-600 uppercase mb-1">Positive Factors</p>
                  <ul className="text-xs text-gray-600 space-y-1">
                    {job.acceptance_factors.positive.map((f, i) => (
                      <li key={i}>+ {f}</li>
                    ))}
                  </ul>
                </div>
              )}
              {job.acceptance_factors.negative?.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-red-600 uppercase mb-1">Risk Factors</p>
                  <ul className="text-xs text-gray-600 space-y-1">
                    {job.acceptance_factors.negative.map((f, i) => (
                      <li key={i}>- {f}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {job.skill_coverage != null && (
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase mb-1">Skill Coverage</p>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-500 h-2 rounded-full transition-all"
                  style={{ width: `${Math.min(100, job.skill_coverage)}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">{job.skill_coverage.toFixed(0)}% of required skills matched</p>
            </div>
          )}
        </div>
      )}

      <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
        <div className="flex gap-2">
          <button
            onClick={() => handleStatus('interested')}
            disabled={updating || job.status === 'interested'}
            className="px-3 py-1.5 text-xs font-medium rounded-lg bg-green-50 text-green-700 hover:bg-green-100 disabled:opacity-50 transition"
          >
            Interested
          </button>
          <button
            onClick={() => handleStatus('applied')}
            disabled={updating || job.status === 'applied'}
            className="px-3 py-1.5 text-xs font-medium rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 disabled:opacity-50 transition"
          >
            Applied
          </button>
          <button
            onClick={() => handleStatus('not_relevant')}
            disabled={updating || job.status === 'not_relevant'}
            className="px-3 py-1.5 text-xs font-medium rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 disabled:opacity-50 transition"
          >
            Not Relevant
          </button>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            {showDetails ? 'Less' : 'More'}
          </button>
          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 text-xs font-medium rounded-lg bg-primary-600 text-white hover:bg-primary-700 transition"
          >
            View &amp; Apply
          </a>
        </div>
      </div>
    </div>
  );
}
