import React from 'react';
import { DocumentUploadBox } from './components/DocumentUpload';
import { SystemHealthMonitor } from './components/SystemHealthMonitor';
import { InteractiveArchitectureDiagram } from './components/ArchitectureDiagram';
import './index.css';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Rwanda NCSA Compliance Auditor
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                AI-Augmented Unified Compliance Auditor v3.0.0
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">ENGINE 6:</span>
              <span className="text-sm font-semibold text-blue-600">Web Dashboard</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Row 1: Document Upload */}
          <section>
            <DocumentUploadBox />
          </section>

          {/* Row 2: System Health Monitor */}
          <section>
            <SystemHealthMonitor />
          </section>

          {/* Row 3: Architecture Diagram */}
          <section>
            <InteractiveArchitectureDiagram />
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <p>
              © 2024 Rwanda NCSA Compliance Auditor | Research Project
            </p>
            <p>
              Built with React 18 + TypeScript + Three.js
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
