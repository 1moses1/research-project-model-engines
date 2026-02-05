import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { Dashboard, AuditWizard, AuditProgress, AuditResults } from './pages';
import { DocumentUploadBox } from './components/DocumentUpload';
import { SystemHealthMonitor } from './components/SystemHealthMonitor';
import { InteractiveArchitectureDiagram } from './components/ArchitectureDiagram';
import './index.css';

// Layout wrapper component
const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link to="/dashboard" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Rwanda NCSA Compliance Auditor
                </h1>
                <p className="text-xs text-gray-500">
                  AI-Augmented Unified Compliance Auditor v3.0.0
                </p>
              </div>
            </Link>
            <nav className="flex items-center gap-6">
              <Link
                to="/dashboard"
                className="text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors"
              >
                Dashboard
              </Link>
              <Link
                to="/audit/new"
                className="text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors"
              >
                New Audit
              </Link>
              <Link
                to="/system"
                className="text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors"
              >
                System
              </Link>
              <div className="flex items-center gap-2 pl-4 border-l">
                <span className="text-xs text-gray-500">ENGINE 6:</span>
                <span className="text-xs font-semibold text-blue-600">Web Dashboard</span>
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <p>
              2024-2026 Rwanda NCSA Compliance Auditor | Research Project
            </p>
            <p>
              Built with React 18 + TypeScript + FastAPI
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// System page with existing components
const SystemPage: React.FC = () => {
  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">System Overview</h1>

      {/* Document Upload */}
      <section>
        <DocumentUploadBox />
      </section>

      {/* System Health Monitor */}
      <section>
        <SystemHealthMonitor />
      </section>

      {/* Architecture Diagram */}
      <section>
        <InteractiveArchitectureDiagram />
      </section>
    </div>
  );
};

// Upload page
const UploadPage: React.FC = () => {
  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">Upload Documents & Logs</h1>
      <DocumentUploadBox />
    </div>
  );
};

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          {/* Default redirect to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* Main dashboard */}
          <Route path="/dashboard" element={<Dashboard />} />

          {/* Audit workflow */}
          <Route path="/audit/new" element={<AuditWizard />} />
          <Route path="/audit/:auditId/progress" element={<AuditProgress />} />
          <Route path="/audit/:auditId/results" element={<AuditResults />} />

          {/* Upload page */}
          <Route path="/upload" element={<UploadPage />} />

          {/* System overview (original components) */}
          <Route path="/system" element={<SystemPage />} />

          {/* Audits list (redirects to dashboard for now) */}
          <Route path="/audits" element={<Navigate to="/dashboard" replace />} />
          <Route path="/reports" element={<Navigate to="/dashboard" replace />} />

          {/* 404 fallback */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
