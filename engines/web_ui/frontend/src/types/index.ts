export interface UploadedFile {
  name: string;
  size: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  extractedControls?: number;
  error?: string;
}

export interface SystemStatus {
  mcp_server: {
    status: 'connected' | 'disconnected' | 'error';
    logs_per_second: number;
    active_connectors: string[];
    uptime_seconds: number;
  };
  databases: {
    postgresql: {
      status: 'healthy' | 'degraded' | 'down';
      connections: number;
      query_latency_ms: number;
    };
    redis: {
      status: 'healthy' | 'degraded' | 'down';
      memory_usage_mb: number;
      hit_rate_percent: number;
    };
  };
  engines: {
    [key: string]: {
      status: 'running' | 'stopped' | 'error';
      requests_per_minute: number;
      avg_latency_ms: number;
    };
  };
  cache_performance: {
    hit_rate: number;
    total_size_mb: number;
    evictions_per_minute: number;
  };
}

export interface EngineNode {
  id: string;
  name: string;
  position: [number, number, number];
  status: 'running' | 'stopped' | 'error';
  connections: string[];
  metrics: {
    requests_per_minute: number;
    avg_latency_ms: number;
  };
}
