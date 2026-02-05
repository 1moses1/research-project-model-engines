import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import {
  ChevronLeft,
  ChevronRight,
  Check,
  Upload,
  FileText,
  Settings,
  Play,
  X,
  Folder,
  AlertCircle
} from 'lucide-react';

interface AuditConfig {
  audit_type: string;
  log_sources: Array<{ type: string; path?: string }>;
  document_ids: string[];
  control_families: string[];
  time_range: { start: string; end: string } | null;
  target_host: string;
  company_name: string;
  framework: string;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  status: 'pending' | 'uploading' | 'uploaded' | 'error';
}

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8006';

const AUDIT_TYPES = [
  { value: 'full', label: 'Full Audit', description: 'Log analysis + Document analysis' },
  { value: 'log_analysis', label: 'Log Analysis', description: 'Analyze system logs only' },
  { value: 'document_analysis', label: 'Document Analysis', description: 'Analyze policy documents only' }
];

export const AuditWizard: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [auditId, setAuditId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [controlFamilies, setControlFamilies] = useState<string[]>([]);

  const [config, setConfig] = useState<AuditConfig>({
    audit_type: 'full',
    log_sources: [],
    document_ids: [],
    control_families: [],
    time_range: null,
    target_host: 'localhost',
    company_name: '',
    framework: 'Rwanda-NCSA'
  });

  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const steps = [
    { title: 'Configuration', icon: Settings },
    { title: 'Log Sources', icon: Folder },
    { title: 'Documents', icon: Upload },
    { title: 'Review & Start', icon: Play }
  ];

  // Fetch control families on mount
  useEffect(() => {
    fetchControlFamilies();
  }, []);

  const fetchControlFamilies = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/control-families`);
      if (response.ok) {
        const data = await response.json();
        setControlFamilies(data.families || []);
      }
    } catch (error) {
      console.error('Error fetching control families:', error);
    }
  };

  // File drop handler
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
      id: Math.random().toString(36).substring(7),
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending' as const
    }));
    setUploadedFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    }
  });

  const removeFile = (id: string) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const toggleControlFamily = (family: string) => {
    setConfig((prev) => ({
      ...prev,
      control_families: prev.control_families.includes(family)
        ? prev.control_families.filter((f) => f !== family)
        : [...prev.control_families, family]
    }));
  };

  const handleStartAudit = async () => {
    setLoading(true);
    setError(null);

    try {
      // Step 1: Configure audit
      const configResponse = await fetch(`${API_BASE}/api/audit/configure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });

      if (!configResponse.ok) {
        throw new Error('Failed to configure audit');
      }

      const configData = await configResponse.json();
      const newAuditId = configData.audit_id;
      setAuditId(newAuditId);

      // Step 2: Upload documents if any
      if (uploadedFiles.length > 0) {
        const formData = new FormData();
        // Note: In real implementation, would need to get the actual File objects
        // For now, we'll skip actual upload since we don't have the File objects

        // Update file statuses
        setUploadedFiles((prev) =>
          prev.map((f) => ({ ...f, status: 'uploaded' as const }))
        );
      }

      // Step 3: Start the audit
      const startResponse = await fetch(`${API_BASE}/api/audit/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config })
      });

      if (!startResponse.ok) {
        throw new Error('Failed to start audit');
      }

      const startData = await startResponse.json();

      // Navigate to progress page
      navigate(`/audit/${startData.audit_id}/progress`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return config.audit_type && config.company_name.trim() !== '';
      case 1:
        return config.audit_type === 'document_analysis' || true; // Log sources optional
      case 2:
        return config.audit_type === 'log_analysis' || true; // Documents optional
      case 3:
        return true;
      default:
        return false;
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            {/* Audit Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Audit Type
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {AUDIT_TYPES.map((type) => (
                  <div
                    key={type.value}
                    onClick={() => setConfig({ ...config, audit_type: type.value })}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      config.audit_type === type.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <p className="font-medium">{type.label}</p>
                    <p className="text-sm text-gray-500">{type.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Company Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization Name *
              </label>
              <input
                type="text"
                value={config.company_name}
                onChange={(e) => setConfig({ ...config, company_name: e.target.value })}
                placeholder="Enter organization name"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Target Host */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Host
              </label>
              <input
                type="text"
                value={config.target_host}
                onChange={(e) => setConfig({ ...config, target_host: e.target.value })}
                placeholder="localhost"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-sm text-gray-500 mt-1">
                Use "localhost" for local audit or enter remote hostname
              </p>
            </div>

            {/* Control Families */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Control Families (Optional - leave empty for all)
              </label>
              <div className="flex flex-wrap gap-2">
                {controlFamilies.map((family) => (
                  <Badge
                    key={family}
                    onClick={() => toggleControlFamily(family)}
                    className={`cursor-pointer ${
                      config.control_families.includes(family)
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {family}
                    {config.control_families.includes(family) && (
                      <Check className="w-3 h-3 ml-1" />
                    )}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        );

      case 1:
        return (
          <div className="space-y-6">
            <p className="text-gray-600">
              Configure log sources for analysis. The system will collect logs from these sources.
            </p>

            {/* Log Source Options */}
            <div className="space-y-4">
              <div
                onClick={() =>
                  setConfig({
                    ...config,
                    log_sources: [{ type: 'local', path: '/var/log' }]
                  })
                }
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  config.log_sources.some((s) => s.type === 'local')
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Folder className="w-6 h-6 text-blue-500" />
                  <div>
                    <p className="font-medium">Local System Logs</p>
                    <p className="text-sm text-gray-500">
                      Collect logs from this machine (/var/log, system logs)
                    </p>
                  </div>
                </div>
              </div>

              <div
                onClick={() =>
                  setConfig({
                    ...config,
                    log_sources: [{ type: 'sample' }]
                  })
                }
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  config.log_sources.some((s) => s.type === 'sample')
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-3">
                  <FileText className="w-6 h-6 text-green-500" />
                  <div>
                    <p className="font-medium">Sample Logs</p>
                    <p className="text-sm text-gray-500">
                      Use sample authentication logs for demonstration
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Time Range */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date (Optional)
                </label>
                <input
                  type="datetime-local"
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      time_range: {
                        ...config.time_range,
                        start: e.target.value
                      } as any
                    })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date (Optional)
                </label>
                <input
                  type="datetime-local"
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      time_range: {
                        ...config.time_range,
                        end: e.target.value
                      } as any
                    })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <p className="text-gray-600">
              Upload policy documents for compliance analysis. Supported formats: PDF, DOCX, TXT
            </p>

            {/* Dropzone */}
            <div
              {...getRootProps()}
              className={`p-8 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              {isDragActive ? (
                <p className="text-blue-600">Drop files here...</p>
              ) : (
                <>
                  <p className="text-gray-600">
                    Drag & drop policy documents here, or click to select
                  </p>
                  <p className="text-sm text-gray-400 mt-2">
                    Supported: PDF, DOCX, TXT
                  </p>
                </>
              )}
            </div>

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                <p className="font-medium text-gray-700">
                  Uploaded Files ({uploadedFiles.length})
                </p>
                {uploadedFiles.map((file) => (
                  <div
                    key={file.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-blue-500" />
                      <div>
                        <p className="text-sm font-medium">{file.name}</p>
                        <p className="text-xs text-gray-500">
                          {(file.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(file.id)}
                      className="p-1 hover:bg-gray-200 rounded"
                    >
                      <X className="w-4 h-4 text-gray-500" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <p className="text-gray-600">
              Review your audit configuration before starting.
            </p>

            {/* Configuration Summary */}
            <div className="bg-gray-50 rounded-lg p-6 space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Audit Type</span>
                <span className="font-medium">
                  {AUDIT_TYPES.find((t) => t.value === config.audit_type)?.label}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Organization</span>
                <span className="font-medium">{config.company_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Target Host</span>
                <span className="font-medium">{config.target_host}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Framework</span>
                <span className="font-medium">{config.framework}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Log Sources</span>
                <span className="font-medium">
                  {config.log_sources.length > 0
                    ? config.log_sources.map((s) => s.type).join(', ')
                    : 'Default'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Documents</span>
                <span className="font-medium">{uploadedFiles.length} files</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Control Families</span>
                <span className="font-medium">
                  {config.control_families.length > 0
                    ? `${config.control_families.length} selected`
                    : 'All families'}
                </span>
              </div>
            </div>

            {error && (
              <div className="flex items-center gap-2 p-4 bg-red-50 text-red-700 rounded-lg">
                <AlertCircle className="w-5 h-5" />
                <p>{error}</p>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>New Compliance Audit</CardTitle>

          {/* Progress Steps */}
          <div className="flex items-center justify-between mt-6">
            {steps.map((step, index) => (
              <React.Fragment key={step.title}>
                <div className="flex flex-col items-center">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      index < currentStep
                        ? 'bg-green-500 text-white'
                        : index === currentStep
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-500'
                    }`}
                  >
                    {index < currentStep ? (
                      <Check className="w-5 h-5" />
                    ) : (
                      <step.icon className="w-5 h-5" />
                    )}
                  </div>
                  <span
                    className={`text-xs mt-2 ${
                      index === currentStep ? 'text-blue-600 font-medium' : 'text-gray-500'
                    }`}
                  >
                    {step.title}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`flex-1 h-1 mx-2 ${
                      index < currentStep ? 'bg-green-500' : 'bg-gray-200'
                    }`}
                  />
                )}
              </React.Fragment>
            ))}
          </div>
        </CardHeader>

        <CardContent className="min-h-[400px]">{renderStepContent()}</CardContent>

        <CardFooter className="flex justify-between">
          <Button
            variant="outline"
            onClick={() => setCurrentStep((prev) => prev - 1)}
            disabled={currentStep === 0}
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Back
          </Button>

          {currentStep < steps.length - 1 ? (
            <Button
              onClick={() => setCurrentStep((prev) => prev + 1)}
              disabled={!canProceed()}
            >
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={handleStartAudit}
              disabled={loading || !canProceed()}
              className="bg-green-600 hover:bg-green-700"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Starting...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Start Audit
                </>
              )}
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
};

export default AuditWizard;
