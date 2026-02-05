import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend
} from 'recharts';
import {
  ArrowLeft,
  Download,
  FileText,
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  Eye,
  Mail
} from 'lucide-react';

interface AuditSummary {
  compliance_rate: number;
  risk_level: string;
  total_controls: number;
  compliant: number;
  non_compliant: number;
  partial: number;
  logs_analyzed?: number;
  documents_analyzed?: number;
}

interface AuditResult {
  audit_id: string;
  status: string;
  summary: AuditSummary;
  log_analysis: Array<{
    source_id: string;
    raw_message: string;
    status: string;
    control_id: string;
    control_family: string;
    confidence: number;
  }>;
  document_analysis: Array<{
    doc_id: string;
    filename: string;
    controls_found: number;
  }>;
  control_families: Record<
    string,
    { compliant: number; non_compliant: number; partial: number }
  >;
  timestamp?: string;
}

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8006';

const COLORS = {
  compliant: '#22c55e',
  non_compliant: '#ef4444',
  partial: '#eab308',
  unknown: '#9ca3af'
};

export const AuditResults: React.FC = () => {
  const { auditId } = useParams<{ auditId: string }>();
  const [results, setResults] = useState<AuditResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedFamily, setExpandedFamily] = useState<string | null>(null);
  const [showAllFindings, setShowAllFindings] = useState(false);

  useEffect(() => {
    if (auditId) {
      fetchResults();
    }
  }, [auditId]);

  const fetchResults = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/audit/${auditId}/results`);
      if (response.ok) {
        setResults(await response.json());
      }
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (format: string) => {
    try {
      const response = await fetch(
        `${API_BASE}/api/audit/${auditId}/report/download?format=${format}`
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `compliance_report_${auditId}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error downloading report:', error);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'LOW':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'HIGH':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'non_compliant':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'partial':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default:
        return <Shield className="w-4 h-4 text-gray-400" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (!results) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Audit results not found</p>
        <Link to="/dashboard">
          <Button variant="outline" className="mt-4">
            Return to Dashboard
          </Button>
        </Link>
      </div>
    );
  }

  // Prepare chart data
  const pieData = [
    { name: 'Compliant', value: results.summary.compliant, color: COLORS.compliant },
    { name: 'Non-Compliant', value: results.summary.non_compliant, color: COLORS.non_compliant },
    { name: 'Partial', value: results.summary.partial || 0, color: COLORS.partial }
  ].filter((d) => d.value > 0);

  const familyData = Object.entries(results.control_families || {}).map(([name, data]) => ({
    name: name.length > 15 ? name.substring(0, 15) + '...' : name,
    fullName: name,
    compliant: data.compliant,
    non_compliant: data.non_compliant,
    partial: data.partial || 0
  }));

  const displayedFindings = showAllFindings
    ? results.log_analysis
    : results.log_analysis?.slice(0, 10);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/dashboard">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Audit Results</h1>
            <p className="text-sm text-gray-600">{auditId}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => handleDownload('json')}>
            <Download className="w-4 h-4 mr-2" />
            JSON
          </Button>
          <Button onClick={() => handleDownload('pdf')}>
            <Download className="w-4 h-4 mr-2" />
            PDF Report
          </Button>
        </div>
      </div>

      {/* Executive Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Executive Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {/* Compliance Rate */}
            <div className="text-center">
              <div className="relative inline-flex items-center justify-center w-24 h-24">
                <svg className="w-24 h-24 transform -rotate-90">
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="#e5e7eb"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke={
                      results.summary.compliance_rate >= 80
                        ? '#22c55e'
                        : results.summary.compliance_rate >= 60
                        ? '#eab308'
                        : '#ef4444'
                    }
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${results.summary.compliance_rate * 2.51} 251`}
                    strokeLinecap="round"
                  />
                </svg>
                <span className="absolute text-2xl font-bold">
                  {results.summary.compliance_rate?.toFixed(0)}%
                </span>
              </div>
              <p className="text-sm text-gray-500 mt-2">Compliance Rate</p>
            </div>

            {/* Risk Level */}
            <div className="text-center">
              <div
                className={`inline-block px-6 py-4 rounded-lg border-2 ${getRiskColor(
                  results.summary.risk_level
                )}`}
              >
                <p className="text-2xl font-bold">{results.summary.risk_level}</p>
              </div>
              <p className="text-sm text-gray-500 mt-2">Risk Level</p>
            </div>

            {/* Total Controls */}
            <div className="text-center">
              <p className="text-4xl font-bold text-gray-900">
                {results.summary.total_controls}
              </p>
              <p className="text-sm text-gray-500 mt-2">Total Controls</p>
            </div>

            {/* Items Analyzed */}
            <div className="text-center">
              <p className="text-4xl font-bold text-blue-600">
                {(results.summary.logs_analyzed || results.log_analysis?.length || 0) +
                  (results.summary.documents_analyzed ||
                    results.document_analysis?.length ||
                    0)}
              </p>
              <p className="text-sm text-gray-500 mt-2">Items Analyzed</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Compliance Distribution Pie */}
        <Card>
          <CardHeader>
            <CardTitle>Compliance Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-6 mt-4">
              {pieData.map((entry) => (
                <div key={entry.name} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: entry.color }}
                  />
                  <span className="text-sm text-gray-600">
                    {entry.name} ({entry.value})
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Control Families Bar Chart */}
        <Card>
          <CardHeader>
            <CardTitle>By Control Family</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={familyData} layout="vertical">
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={100} fontSize={12} />
                  <Tooltip
                    content={({ payload }) => {
                      if (payload && payload.length > 0) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-white p-2 shadow rounded border">
                            <p className="font-medium">{data.fullName}</p>
                            <p className="text-green-600">Compliant: {data.compliant}</p>
                            <p className="text-red-600">Non-Compliant: {data.non_compliant}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="compliant" stackId="a" fill={COLORS.compliant} />
                  <Bar dataKey="non_compliant" stackId="a" fill={COLORS.non_compliant} />
                  <Bar dataKey="partial" stackId="a" fill={COLORS.partial} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Findings Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Detailed Findings</span>
            <Badge variant="outline">{results.log_analysis?.length || 0} items</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    #
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Log Message
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Control
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Confidence
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {displayedFindings?.map((finding, index) => (
                  <tr key={finding.source_id || index} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-500">{index + 1}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 max-w-md truncate">
                      {finding.raw_message?.substring(0, 80)}...
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(finding.status)}
                        <span
                          className={`text-sm capitalize ${
                            finding.status === 'compliant'
                              ? 'text-green-700'
                              : finding.status === 'non_compliant'
                              ? 'text-red-700'
                              : 'text-gray-700'
                          }`}
                        >
                          {finding.status?.replace('_', ' ')}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant="outline">{finding.control_id}</Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Progress value={finding.confidence * 100} className="w-20 h-2" />
                      <span className="text-xs text-gray-500 ml-2">
                        {(finding.confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {results.log_analysis?.length > 10 && (
            <div className="mt-4 text-center">
              <Button
                variant="outline"
                onClick={() => setShowAllFindings(!showAllFindings)}
              >
                {showAllFindings ? (
                  <>
                    <ChevronUp className="w-4 h-4 mr-2" />
                    Show Less
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-4 h-4 mr-2" />
                    Show All ({results.log_analysis.length})
                  </>
                )}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Documents Analyzed */}
      {results.document_analysis && results.document_analysis.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Documents Analyzed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.document_analysis.map((doc, index) => (
                <div
                  key={doc.doc_id || index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-blue-500" />
                    <span className="font-medium">{doc.filename}</span>
                  </div>
                  <Badge variant="outline">{doc.controls_found} controls</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-4 justify-center">
            <Button variant="outline" onClick={() => window.print()}>
              <FileText className="w-4 h-4 mr-2" />
              Print Report
            </Button>
            <Button variant="outline" onClick={() => handleDownload('json')}>
              <Download className="w-4 h-4 mr-2" />
              Export JSON
            </Button>
            <Button onClick={() => handleDownload('pdf')}>
              <Download className="w-4 h-4 mr-2" />
              Download PDF
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuditResults;
