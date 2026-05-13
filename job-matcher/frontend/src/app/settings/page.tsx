'use client';

import { useState, useEffect } from 'react';
import { fetchProfile, uploadCV, uploadLinkedInExport, updatePreferences, Profile } from '@/lib/api';

export default function SettingsPage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const [targetRoles, setTargetRoles] = useState('');
  const [targetLocations, setTargetLocations] = useState('');
  const [workMode, setWorkMode] = useState('any');
  const [minSalary, setMinSalary] = useState('');
  const [salaryCurrency, setSalaryCurrency] = useState('USD');
  const [dealBreakers, setDealBreakers] = useState('');
  const [targetSeniority, setTargetSeniority] = useState<string[]>([]);

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    try {
      const data = await fetchProfile();
      setProfile(data);
      const roles = data.target_roles;
      if (roles) {
        const roleList = Array.isArray(roles) ? roles : roles.roles || [];
        setTargetRoles(roleList.join(', '));
      }
      const locs = data.target_locations;
      if (locs) {
        const locList = Array.isArray(locs) ? locs : locs.locations || [];
        setTargetLocations(locList.join(', '));
      }
      setWorkMode(data.work_mode || 'any');
      setMinSalary(data.min_salary?.toString() || '');
      setSalaryCurrency(data.salary_currency || 'USD');
    } catch (e) {
      // No profile yet
    } finally {
      setLoading(false);
    }
  }

  async function handleCVUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setMessage('');
    try {
      const data = await uploadCV(file);
      setProfile(data);
      setMessage('CV uploaded and parsed successfully!');
    } catch (err) {
      setMessage('Failed to upload CV. Please try again.');
    } finally {
      setUploading(false);
    }
  }

  async function handleLinkedInUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setMessage('');
    try {
      const data = await uploadLinkedInExport(file);
      setProfile(data);
      setMessage('LinkedIn export processed successfully!');
    } catch (err) {
      setMessage('Failed to process LinkedIn export. Please try again.');
    } finally {
      setUploading(false);
    }
  }

  async function handleSavePreferences(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      const prefs: any = {
        work_mode: workMode,
        salary_currency: salaryCurrency,
      };
      if (targetRoles) prefs.target_roles = targetRoles.split(',').map(s => s.trim()).filter(Boolean);
      if (targetLocations) prefs.target_locations = targetLocations.split(',').map(s => s.trim()).filter(Boolean);
      if (minSalary) prefs.min_salary = parseInt(minSalary);
      if (dealBreakers) prefs.deal_breakers = dealBreakers.split(',').map(s => s.trim()).filter(Boolean);
      if (targetSeniority.length) prefs.target_seniority = targetSeniority;

      const data = await updatePreferences(prefs);
      setProfile(data);
      setMessage('Preferences saved!');
    } catch (err) {
      setMessage('Failed to save preferences.');
    } finally {
      setSaving(false);
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
    <div className="space-y-8 max-w-3xl">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
        <p className="text-gray-600 mt-1">Manage your profile and job search preferences</p>
      </div>

      {message && (
        <div className={`px-4 py-3 rounded-lg text-sm ${message.includes('Failed') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
          {message}
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Source</h3>

        {profile && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <p className="font-medium text-gray-900">{profile.name || 'Profile loaded'}</p>
            {profile.headline && <p className="text-sm text-gray-600">{profile.headline}</p>}
            {profile.location && <p className="text-sm text-gray-500">{profile.location}</p>}
            {profile.cv_filename && <p className="text-xs text-gray-400 mt-2">CV: {profile.cv_filename}</p>}
            {profile.linkedin_export_filename && <p className="text-xs text-gray-400">LinkedIn: {profile.linkedin_export_filename}</p>}
            {profile.years_experience && <p className="text-xs text-gray-400">{profile.years_experience} years experience</p>}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Upload CV (PDF or DOCX)</label>
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleCVUpload}
              disabled={uploading}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 disabled:opacity-50"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">LinkedIn Data Export (ZIP)</label>
            <input
              type="file"
              accept=".zip"
              onChange={handleLinkedInUpload}
              disabled={uploading}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 disabled:opacity-50"
            />
            <p className="text-xs text-gray-400 mt-1">LinkedIn Settings &rarr; Get a copy of your data</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSavePreferences} className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Search Preferences</h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Roles</label>
            <input
              type="text"
              value={targetRoles}
              onChange={(e) => setTargetRoles(e.target.value)}
              placeholder="e.g. Software Engineer, Backend Developer, Full Stack Engineer"
              className="w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm"
            />
            <p className="text-xs text-gray-400 mt-1">Comma-separated list of target job titles</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Locations</label>
            <input
              type="text"
              value={targetLocations}
              onChange={(e) => setTargetLocations(e.target.value)}
              placeholder="e.g. Remote, Berlin, London, Dubai"
              className="w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Work Mode</label>
              <select
                value={workMode}
                onChange={(e) => setWorkMode(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm"
              >
                <option value="any">Any</option>
                <option value="remote">Remote Only</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">Onsite</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Minimum Salary</label>
              <input
                type="number"
                value={minSalary}
                onChange={(e) => setMinSalary(e.target.value)}
                placeholder="e.g. 80000"
                className="w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Currency</label>
              <select
                value={salaryCurrency}
                onChange={(e) => setSalaryCurrency(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="EGP">EGP</option>
                <option value="AED">AED</option>
                <option value="SAR">SAR</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Target Seniority</label>
            <div className="flex flex-wrap gap-2">
              {['junior', 'mid', 'senior', 'lead', 'principal', 'manager', 'director'].map((level) => (
                <label key={level} className="flex items-center gap-1.5">
                  <input
                    type="checkbox"
                    checked={targetSeniority.includes(level)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setTargetSeniority([...targetSeniority, level]);
                      } else {
                        setTargetSeniority(targetSeniority.filter(s => s !== level));
                      }
                    }}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm text-gray-700 capitalize">{level}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Deal Breakers</label>
            <input
              type="text"
              value={dealBreakers}
              onChange={(e) => setDealBreakers(e.target.value)}
              placeholder="e.g. crypto, gambling, defense"
              className="w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm"
            />
            <p className="text-xs text-gray-400 mt-1">Jobs containing these terms will be excluded</p>
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="mt-6 px-6 py-2.5 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50 transition"
        >
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </form>
    </div>
  );
}
