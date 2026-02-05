import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { io, Socket } from 'socket.io-client';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import {
  CheckCircle,
  Clock,
  AlertTriangle,
  XCircle,
  FileText,
  Shield,
  Activity,
  ChevronRight,
  RefreshCw,
  StopCircle
} from 'lucide-react';

interface AuditState {
  audit_id: string;
  status: string;
  progress: number;
  current_stage: string;
  message: string;
  started_at?: string;
  results?: {
    summary?: {
      compliance_rate: number;
      risk_level: string;
      total_controls: number;
      compliant: number;
      non_compliant: number;
    };
    log_analysis?: Array<any>;
    document_analysis?: Array<any>;
    control_families?: Record<string, any>;
  };
  error?: string;
}

interface LogEntry {
  timestamp: string;
  stage: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8006';
const WS_BASE = process.env.REACT_APP_WS_URL || 'http://localhost:8006';

const STAGES = [
  { key: 'initializing', label: 'Initializing', icon: Clock },
  { key: 'authenticating', label: 'Authenticating', icon: Shield },
  { key: 'collecting_logs', label: 'Collecting Logs', icon: FileText },
  { key: 'processing_documents', label: 'Processing Documents', icon: FileText },
  { key: 'analyzing', label: 'Analyzing', icon: Activity },
  { key: 'making_decisions', label: 'Making Decisions', icon: Shield },
  { key: 'generating_report', label: 'Generating Report', icon: FileText },
  { key: 'completed', label: 'Completed', icon: CheckCircle }
];

export const AuditProgress: React.FC = () => {
  const { auditId } = useParams<{ auditId: string }>();
  const navigate = useNavigate();
  const [auditState, setAuditState] = useState<AuditState | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<Socket | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!auditId) return;

    // Fetch initial state
    fetchAuditStatus();

    // Connect to WebSocket
    connectWebSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [auditId]);

  useEffect(() => {
    // Auto-scroll logs
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const fetchAuditStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/audit/${auditId}/status`);
      if (response.ok) {
        const data = await response.json();
        setAuditState(data);
        addLog(data.current_stage, data.message, 'info');
      }
    } catch (error) {
      console.error('Error fetching audit status:', error);
    }
  };

  const connectWebSocket = () => {
    const socket = io(WS_BASE, {
      transports: ['websocket', 'polling']
    });

    socket.on('connect', () => {
      setConnected(true);
      console.log('Connected to WebSocket');

      // Subscribe to audit updates
      socket.emit('subscribe_audit', { audit_id: auditId });
    });

    socket.on('disconnect', () => {
      setConnected(false);
      console.log('Disconnected from WebSocket');
    });

    socket.on('audit_update', (data: AuditState) => {
      if (data.audit_id === auditId) {
        setAuditState(data);
        addLog(data.current_stage, data.message, getLogType(data.status));
      }
    });

    socketRef.current = socket;
  };

  const addLog = (stage: string, message: string, type: LogEntry['type']) => {
    setLogs((prev) => [
      ...prev.slice(-99), // Keep last 100 logs
      {
        timestamp: new Date().toISOString(),
        stage,
        message,
        type
      }
    ]);
  };

  const getLogType = (status: string): LogEntry['type'] => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
      case 'error':
        return 'error';
      case 'cancelled':
        return 'warning';
      default:
        return 'info';
    }
  };

  const handleCancel = async () => {
    if (!auditId) return;

    try {
      await fetch(`${API_BASE}/api/audit/${auditId}/cancel`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Error cancelling audit:', error);
    }
  };

  const getCurrentStageIndex = () => {
    if (!auditState) return 0;
    const index = STAGES.findIndex(
      (s) =>
        s.key === auditState.current_stage ||
        auditState.current_stage.includes(s.key)
    );
    return Math.max(0, index);
  };

  const isCompleted = auditState?.status === 'completed';
  const isFailed = auditState?.status === 'failed';
  const isRunning = auditState?.status === 'running';

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Progress</h1>
          <p className="text-sm text-gray-600">{auditId}</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Connection Status */}
          <Badge
            className={connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}
          >
            {connected ? 'Connected' : 'Disconnected'}
          </Badge>

          {isRunning && (
            <Button variant="destructive" onClick={handleCancel}>
              <StopCircle className="w-4 h-4 mr-2" />
              Cancel
            </Button>
          )}

          {isCompleted && (
            <Link to={`/audit/${auditId}/results`}>
              <Button>
                View Results
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          )}
        </div>
      </div>

      {/* Progress Overview */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4">
            {/* Progress Bar */}
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">
                {auditState?.current_stage?.replace(/_/g, ' ').toUpperCase() || 'INITIALIZING'}
              </span>
              <span className="text-sm text-gray-500">{auditState?.progress || 0}%</span>
            </div>
            <Progress value={auditState?.progress || 0} className="h-3" />

            {/* Status Message */}
            <div className="flex items-center gap-2 mt-4">
              {isCompleted ? (
                <CheckCircle className="w-5 h-5 text-green-500" />
              ) : isFailed ? (
                <XCircle className="w-5 h-5 text-red-500" />
              ) : (
                <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />
              )}
              <span
                className={`font-medium ${
                  isCompleted
                    ? 'text-green-700'
                    : isFailed
                    ? 'text-red-700'
                    : 'text-blue-700'
                }`}
              >
                {auditState?.message || 'Initializing...'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stages Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Pipeline Stages</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            {STAGES.map((stage, index) => {
              const currentIndex = getCurrentStageIndex();
              const isActive = index === currentIndex;
              const isComplete = index < currentIndex || isCompleted;
              const Icon = stage.icon;

              return (
                <div key={stage.key} className="flex items-start mb-4 last:mb-0">
                  {/* Timeline Line */}
                  {index < STAGES.length - 1 && (
                    <div
                      className={`absolute left-5 w-0.5 h-full mt-10 ${
                        isComplete ? 'bg-green-500' : 'bg-gray-200'
                      }`}
                      style={{ top: `${index * 52}px`, height: '52px' }}
                    />
                  )}

                  {/* Stage Icon */}
                  <div
                    className={`relative z-10 w-10 h-10 rounded-full flex items-center justify-center ${
                      isComplete
                        ? 'bg-green-500 text-white'
                        : isActive
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-500'
                    }`}
                  >
                    {isComplete ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : isActive ? (
                      <RefreshCw className="w-5 h-5 animate-spin" />
                    ) : (
                      <Icon className="w-5 h-5" />
                    )}
                  </div>

                  {/* Stage Info */}
                  <div className="ml-4 pt-2">
                    <p
                      className={`font-medium ${
                        isActive ? 'text-blue-700' : isComplete ? 'text-green-700' : 'text-gray-500'
                      }`}
                    >
                      {stage.label}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Summary (when completed) */}
      {isCompleted && auditState?.results?.summary && (
        <Card>
          <CardHeader>
            <CardTitle>Quick Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">
                  {auditState.results.summary.compliance_rate?.toFixed(1)}%
                </p>
                <p className="text-sm text-gray-500">Compliance</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <Badge
                  className={`text-lg ${
                    auditState.results.summary.risk_level === 'LOW'
                      ? 'bg-green-100 text-green-800'
                      : auditState.results.summary.risk_level === 'MEDIUM'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {auditState.results.summary.risk_level}
                </Badge>
                <p className="text-sm text-gray-500 mt-2">Risk Level</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">
                  {auditState.results.summary.compliant}
                </p>
                <p className="text-sm text-gray-500">Compliant</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-red-600">
                  {auditState.results.summary.non_compliant}
                </p>
                <p className="text-sm text-gray-500">Non-Compliant</p>
              </div>
            </div>

            <div className="mt-6 flex justify-center">
              <Link to={`/audit/${auditId}/results`}>
                <Button size="lg">
                  View Full Results
                  <ChevronRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {isFailed && auditState?.error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-6 h-6 text-red-500 flex-shrink-0" />
              <div>
                <p className="font-medium text-red-800">Audit Failed</p>
                <p className="text-sm text-red-600 mt-1">{auditState.error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Live Logs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Live Logs</span>
            <Badge variant="outline">{logs.length} entries</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-900 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
            {logs.length === 0 ? (
              <p className="text-gray-500">Waiting for logs...</p>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="flex gap-2 mb-1">
                  <span className="text-gray-500">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span
                    className={`${
                      log.type === 'success'
                        ? 'text-green-400'
                        : log.type === 'error'
                        ? 'text-red-400'
                        : log.type === 'warning'
                        ? 'text-yellow-400'
                        : 'text-blue-400'
                    }`}
                  >
                    [{log.stage}]
                  </span>
                  <span className="text-gray-300">{log.message}</span>
                </div>
              ))
            )}
            <div ref={logsEndRef} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuditProgress;
