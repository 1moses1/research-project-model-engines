import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, Database, Zap, Server, Cloud } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { SystemStatus } from '@/types';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8006';

export const SystemHealthMonitor: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const { subscribe, isConnected } = useWebSocket();

  useEffect(() => {
    // Subscribe to real-time system status updates
    const unsubscribe = subscribe('system_status', (data: SystemStatus) => {
      setStatus(data);
    });

    // Fetch initial status
    fetchSystemStatus();

    return unsubscribe;
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v3/system/status`);
      setStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  if (!status) {
    return (
      <Card className="w-full">
        <CardContent className="pt-6">
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full" />
            <span className="ml-3 text-gray-600">Loading system status...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getStatusColor = (statusValue: string) => {
    switch (statusValue) {
      case 'connected':
      case 'healthy':
      case 'running':
        return 'bg-green-500 text-white';
      case 'degraded':
        return 'bg-yellow-500 text-white';
      default:
        return 'bg-red-500 text-white';
    }
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          System Health Monitor
          <div className="ml-auto">
            <Badge className={isConnected ? 'bg-green-500' : 'bg-gray-500'}>
              {isConnected ? 'Live' : 'Offline'}
            </Badge>
          </div>
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Real-time monitoring of all system components
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* MCP Server Status */}
        <div className="border rounded-lg p-4 bg-gradient-to-r from-blue-50 to-white">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Cloud className="h-5 w-5 text-blue-600" />
              <h3 className="font-semibold">MCP Log Collection Server</h3>
            </div>
            <Badge className={getStatusColor(status.mcp_server.status)}>
              {status.mcp_server.status}
            </Badge>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Logs/second</p>
              <p className="text-2xl font-bold text-blue-600">
                {status.mcp_server.logs_per_second.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-gray-500">Uptime</p>
              <p className="text-2xl font-bold text-blue-600">
                {formatUptime(status.mcp_server.uptime_seconds)}
              </p>
            </div>
          </div>
          <div className="mt-3">
            <p className="text-sm text-gray-500 mb-2">Active Connectors:</p>
            <div className="flex flex-wrap gap-2">
              {status.mcp_server.active_connectors.map((connector, idx) => (
                <Badge key={idx} variant="outline" className="text-xs">
                  {connector}
                </Badge>
              ))}
            </div>
          </div>
        </div>

        {/* Database Status */}
        <div className="border rounded-lg p-4 bg-gradient-to-r from-purple-50 to-white">
          <div className="flex items-center gap-2 mb-3">
            <Database className="h-5 w-5 text-purple-600" />
            <h3 className="font-semibold">Database Connections</h3>
          </div>

          {/* PostgreSQL */}
          <div className="mb-3 pb-3 border-b">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">PostgreSQL</span>
              <Badge className={getStatusColor(status.databases.postgresql.status)}>
                {status.databases.postgresql.status}
              </Badge>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-500">Connections:</span>
                <span className="ml-2 font-medium">
                  {status.databases.postgresql.connections}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Latency:</span>
                <span className="ml-2 font-medium">
                  {status.databases.postgresql.query_latency_ms}ms
                </span>
              </div>
            </div>
          </div>

          {/* Redis */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">Redis Cache</span>
              <Badge className={getStatusColor(status.databases.redis.status)}>
                {status.databases.redis.status}
              </Badge>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-500">Memory:</span>
                <span className="ml-2 font-medium">
                  {status.databases.redis.memory_usage_mb}MB
                </span>
              </div>
              <div>
                <span className="text-gray-500">Hit Rate:</span>
                <span className="ml-2 font-medium text-green-600">
                  {status.databases.redis.hit_rate_percent}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Cache Performance */}
        <div className="border rounded-lg p-4 bg-gradient-to-r from-yellow-50 to-white">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="h-5 w-5 text-yellow-600" />
            <h3 className="font-semibold">Cache Performance</h3>
          </div>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Hit Rate</p>
              <p className="text-xl font-bold text-green-600">
                {status.cache_performance.hit_rate}%
              </p>
            </div>
            <div>
              <p className="text-gray-500">Size</p>
              <p className="text-xl font-bold">
                {status.cache_performance.total_size_mb}MB
              </p>
            </div>
            <div>
              <p className="text-gray-500">Evictions/min</p>
              <p className="text-xl font-bold">
                {status.cache_performance.evictions_per_minute}
              </p>
            </div>
          </div>
        </div>

        {/* Processing Engines Status */}
        <div className="border rounded-lg p-4 bg-gradient-to-r from-indigo-50 to-white">
          <div className="flex items-center gap-2 mb-3">
            <Server className="h-5 w-5 text-indigo-600" />
            <h3 className="font-semibold">Processing Engines</h3>
          </div>
          <div className="space-y-2">
            {Object.entries(status.engines).map(([name, engine]) => (
              <div key={name} className="flex items-center justify-between text-sm py-2 border-b last:border-b-0">
                <span className="font-medium">{name}</span>
                <div className="flex items-center gap-3">
                  <span className="text-gray-500 text-xs">
                    {engine.requests_per_minute.toLocaleString()} req/min
                  </span>
                  <span className="text-gray-500 text-xs">
                    {engine.avg_latency_ms}ms
                  </span>
                  <Badge className={getStatusColor(engine.status)}>
                    {engine.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Last Updated */}
        <div className="text-xs text-gray-500 text-center">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </CardContent>
    </Card>
  );
};
