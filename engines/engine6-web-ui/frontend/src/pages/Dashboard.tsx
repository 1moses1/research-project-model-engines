import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import {
  Plus,
  FileText,
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Upload,
  Calendar,
  ChevronRight
} from 'lucide-react';

interface StatsOverview {
  compliance_rate: number;
  risk_level: string;
  pending_reviews: number;
  total_audits: number;
  completed_audits: number;
  running_audits: number;
}

interface RecentAudit {
  audit_id: string;
  status: string;
  config: {
    target_host: string;
    company_name?: string;
    framework: string;
  };
  results?: {
    summary?: {
      compliance_rate: number;
      risk_level: string;
      total_controls: number;
    };
  };
  started_at?: string;
  completed_at?: string;
}

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8006';

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [recentAudits, setRecentAudits] = useState<RecentAudit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, auditsRes] = await Promise.all([
        fetch(`${API_BASE}/api/stats/overview`),
        fetch(`${API_BASE}/api/audits/recent?limit=5`)
      ]);

      if (statsRes.ok) {
        setStats(await statsRes.json());
      }
      if (auditsRes.ok) {
        const data = await auditsRes.json();
        setRecentAudits(data.audits || []);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'LOW': return 'bg-green-100 text-green-800';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800';
      case 'HIGH': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'running': return <Clock className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'failed': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      default: return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Dashboard</h1>
          <p className="text-sm text-gray-600">Rwanda NCSA Compliance Auditor</p>
        </div>
        <Link to="/audit/new">
          <Button className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            New Audit
          </Button>
        </Link>
      </div>

      {/* Stats Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Compliance Rate */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Overall Compliance</p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats?.compliance_rate?.toFixed(1) || 0}%
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <Progress value={stats?.compliance_rate || 0} className="mt-3" />
          </CardContent>
        </Card>

        {/* Risk Level */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Risk Level</p>
                <Badge className={`mt-1 ${getRiskColor(stats?.risk_level || '')}`}>
                  {stats?.risk_level || 'UNKNOWN'}
                </Badge>
              </div>
              <div className="p-3 bg-yellow-100 rounded-full">
                <Shield className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Pending Reviews */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Pending Reviews</p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats?.pending_reviews || 0}
                </p>
              </div>
              <div className="p-3 bg-red-100 rounded-full">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Total Audits */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Audits</p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats?.total_audits || 0}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <FileText className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Audits */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Recent Audits</span>
            <Link to="/audits" className="text-sm text-blue-600 hover:underline">
              View All
            </Link>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="py-8 text-center text-gray-500">Loading...</div>
          ) : recentAudits.length === 0 ? (
            <div className="py-8 text-center">
              <p className="text-gray-500 mb-4">No audits yet</p>
              <Link to="/audit/new">
                <Button variant="outline">Start Your First Audit</Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recentAudits.map((audit) => (
                <Link
                  key={audit.audit_id}
                  to={`/audit/${audit.audit_id}/results`}
                  className="block"
                >
                  <div className="flex items-center justify-between p-4 rounded-lg border hover:bg-gray-50 transition-colors">
                    <div className="flex items-center gap-4">
                      {getStatusIcon(audit.status)}
                      <div>
                        <p className="font-medium text-gray-900">
                          {audit.audit_id}
                        </p>
                        <p className="text-sm text-gray-500">
                          {audit.config?.target_host || audit.config?.company_name}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {audit.results?.summary && (
                        <Badge className={getRiskColor(audit.results.summary.risk_level)}>
                          {audit.results.summary.compliance_rate?.toFixed(0)}%
                        </Badge>
                      )}
                      <div className="text-sm text-gray-500 flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {audit.started_at
                          ? new Date(audit.started_at).toLocaleDateString()
                          : 'N/A'}
                      </div>
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Link to="/audit/new">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="pt-6 text-center">
              <Plus className="w-8 h-8 mx-auto text-blue-600 mb-2" />
              <p className="font-medium">New Audit</p>
            </CardContent>
          </Card>
        </Link>
        <Link to="/upload">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="pt-6 text-center">
              <Upload className="w-8 h-8 mx-auto text-green-600 mb-2" />
              <p className="font-medium">Upload Logs</p>
            </CardContent>
          </Card>
        </Link>
        <Link to="/upload">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="pt-6 text-center">
              <FileText className="w-8 h-8 mx-auto text-purple-600 mb-2" />
              <p className="font-medium">Upload Policies</p>
            </CardContent>
          </Card>
        </Link>
        <Link to="/reports">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="pt-6 text-center">
              <TrendingUp className="w-8 h-8 mx-auto text-orange-600 mb-2" />
              <p className="font-medium">View Reports</p>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;
