import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Job Matcher - Personal Job Intelligence',
  description: 'Your personal job-matching system with daily briefings',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <nav className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-2xl">&#127919;</span>
              <h1 className="text-xl font-bold text-gray-900">Job Matcher</h1>
            </div>
            <div className="flex items-center gap-6">
              <a href="/" className="text-sm font-medium text-gray-700 hover:text-primary-600">Dashboard</a>
              <a href="/jobs" className="text-sm font-medium text-gray-700 hover:text-primary-600">Jobs</a>
              <a href="/settings" className="text-sm font-medium text-gray-700 hover:text-primary-600">Settings</a>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-6 py-8">
          {children}
        </main>
      </body>
    </html>
  )
}
