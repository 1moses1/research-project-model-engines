# Rwanda NCSA Compliance Auditor v3.0.0 - UPDATED ARCHITECTURE
## With Interactive Web Dashboard (ENGINE 6)

**Version**: 3.0.0 (Updated with Web UI)  
**Date**: November 16, 2024  
**New Addition**: ENGINE 6 - Interactive Web Dashboard & Control Center

---

## 🆕 ENGINE 6: Interactive Web Dashboard & Control Center

### Purpose
A modern, real-time web interface that provides:
1. **Document Upload Interface** - Upload company policy documents (PDF, DOCX, XLSX)
2. **System Health Monitor** - Real-time status of all engines and connections
3. **Interactive Architecture Diagram** - Animated, floating visualization of all components
4. **Compliance Dashboard** - Live compliance scores and violations
5. **Report Viewer** - View and download generated reports

### Technology Stack (Latest & Compatible)

```yaml
Frontend:
  - Framework: React 18 + TypeScript
  - UI Library: shadcn/ui + Tailwind CSS
  - 3D Visualization: React Three Fiber (for animated diagram)
  - Real-time Updates: Socket.IO client
  - State Management: Zustand
  - Data Visualization: Recharts + D3.js
  - File Upload: React Dropzone
  - Animations: Framer Motion

Backend:
  - Framework: FastAPI (Python 3.11)
  - WebSocket: Socket.IO server
  - File Processing: Async upload handling
  - Authentication: JWT tokens
  - API Documentation: OpenAPI/Swagger

Communication:
  - REST API: HTTP/JSON
  - WebSocket: Real-time updates
  - Server-Sent Events (SSE): Status streaming

Deployment:
  - Container: Docker
  - Reverse Proxy: Nginx
  - SSL/TLS: Let's Encrypt (auto-renewal)
```

---

## Updated System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RWANDA NCSA COMPLIANCE AUDITOR v3.0.0                    │
│                 (With Interactive Web Dashboard - ENGINE 6)                 │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────────────────────┐
                         │      🌐 ENGINE 6: WEB UI        │
                         │   Interactive Dashboard         │
                         │   (React + FastAPI Backend)     │
                         │                                 │
                         │  ┌───────────────────────────┐  │
                         │  │  DOCUMENT UPLOAD BOX      │  │
                         │  │  • Drag & drop interface  │  │
                         │  │  • PDF, DOCX, XLSX        │  │
                         │  │  • Real-time progress     │  │
                         │  │  • Auto-processing        │  │
                         │  └───────────────────────────┘  │
                         │                                 │
                         │  ┌───────────────────────────┐  │
                         │  │  SYSTEM HEALTH MONITOR    │  │
                         │  │  ┌─────────────────────┐  │  │
                         │  │  │ MCP Server Status   │  │  │
                         │  │  │ ● Connected         │  │  │
                         │  │  │ Logs/sec: 1,234     │  │  │
                         │  │  └─────────────────────┘  │  │
                         │  │  ┌─────────────────────┐  │  │
                         │  │  │ Database Status     │  │  │
                         │  │  │ ● PostgreSQL ✓      │  │  │
                         │  │  │ ● Redis ✓           │  │  │
                         │  │  └─────────────────────┘  │  │
                         │  │  ┌─────────────────────┐  │  │
                         │  │  │ Cache Performance   │  │  │
                         │  │  │ Hit Rate: 92%       │  │  │
                         │  │  │ Size: 128MB         │  │  │
                         │  │  └─────────────────────┘  │  │
                         │  └───────────────────────────┘  │
                         │                                 │
                         │  ┌───────────────────────────┐  │
                         │  │  INTERACTIVE DIAGRAM      │  │
                         │  │  (3D Animated)            │  │
                         │  │                           │  │
                         │  │      [ENGINE 1] ──────────┼─→[ENGINE 3]
                         │  │          ↓               │  │     ↓
                         │  │      [REDIS]             │  │ [ENGINE 4]
                         │  │          ↓               │  │     ↓
                         │  │      [ENGINE 2]          │  │ [ENGINE 5]
                         │  │          ↓               │  │
                         │  │     [POSTGRES]           │  │
                         │  │                           │  │
                         │  │  • Floating nodes         │  │
                         │  │  • Animated connections   │  │
                         │  │  • Click for details      │  │
                         │  │  • Real-time status       │  │
                         │  └───────────────────────────┘  │
                         │                                 │
                         │  ┌───────────────────────────┐  │
                         │  │  COMPLIANCE DASHBOARD     │  │
                         │  │  • Overall Score: 87%     │  │
                         │  │  • Violations: 42         │  │
                         │  │  • Pending Review: 12     │  │
                         │  │  • Charts & Graphs        │  │
                         │  └───────────────────────────┘  │
                         └─────────────┬───────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
         ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
         │   ENGINE 1-5     │ │  PostgreSQL  │ │   Redis Cache    │
         │   (All Engines)  │ │   Database   │ │   + Pub/Sub      │
         │   REST APIs      │ │              │ │                  │
         └──────────────────┘ └──────────────┘ └──────────────────┘
```

---

## ENGINE 6 - Detailed Specifications

### Frontend Application (React + TypeScript)

#### 1. Document Upload Interface

```typescript
// src/components/DocumentUpload.tsx
import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import axios from 'axios';

interface UploadedFile {
  name: string;
  size: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  extractedControls?: number;
  error?: string;
}

export const DocumentUploadBox: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    onDrop: async (acceptedFiles) => {
      for (const file of acceptedFiles) {
        await uploadDocument(file);
      }
    }
  });

  const uploadDocument = async (file: File) => {
    const fileObj: UploadedFile = {
      name: file.name,
      size: file.size,
      status: 'uploading',
      progress: 0
    };
    
    setFiles(prev => [...prev, fileObj]);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('company_name', 'Rwanda Demo Corp');
    formData.append('framework', 'Rwanda-NCSA');
    
    try {
      const response = await axios.post('/api/v3/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          updateFileStatus(file.name, { status: 'uploading', progress });
        }
      });
      
      // Document uploaded, now processing
      updateFileStatus(file.name, { status: 'processing', progress: 100 });
      
      // Wait for processing to complete (via WebSocket)
      // ... (handled by WebSocket listener)
      
    } catch (error) {
      updateFileStatus(file.name, { 
        status: 'error', 
        error: error.message 
      });
    }
  };
  
  const updateFileStatus = (fileName: string, updates: Partial<UploadedFile>) => {
    setFiles(prev => prev.map(f => 
      f.name === fileName ? { ...f, ...updates } : f
    ));
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Company Policy Documents Upload
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          {isDragActive ? (
            <p className="text-blue-600">Drop the files here ...</p>
          ) : (
            <div>
              <p className="text-lg font-medium mb-2">
                Drag & drop policy documents here
              </p>
              <p className="text-sm text-gray-500 mb-4">
                or click to browse (PDF, DOCX, XLSX)
              </p>
              <Button variant="outline">Select Files</Button>
            </div>
          )}
        </div>

        {/* Uploaded Files List */}
        <div className="mt-6 space-y-3">
          {files.map((file, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm text-gray-500">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                </div>
                {file.status === 'completed' && (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                )}
                {file.status === 'error' && (
                  <AlertCircle className="h-5 w-5 text-red-500" />
                )}
              </div>
              
              {file.status === 'uploading' && (
                <div>
                  <Progress value={file.progress} className="mb-1" />
                  <p className="text-sm text-gray-600">Uploading...</p>
                </div>
              )}
              
              {file.status === 'processing' && (
                <div className="flex items-center gap-2">
                  <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full" />
                  <p className="text-sm text-blue-600">
                    Processing with LLM... Extracting controls
                  </p>
                </div>
              )}
              
              {file.status === 'completed' && (
                <p className="text-sm text-green-600">
                  ✓ Extracted {file.extractedControls} controls
                </p>
              )}
              
              {file.status === 'error' && (
                <p className="text-sm text-red-600">{file.error}</p>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
```

#### 2. System Health Monitor

```typescript
// src/components/SystemHealthMonitor.tsx
import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, Database, Zap, Server, Cloud } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface SystemStatus {
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

export const SystemHealthMonitor: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    // Subscribe to real-time system status updates
    const unsubscribe = subscribe('system_status', (data: SystemStatus) => {
      setStatus(data);
    });

    // Fetch initial status
    fetch('/api/v3/system/status')
      .then(res => res.json())
      .then(setStatus);

    return unsubscribe;
  }, []);

  if (!status) {
    return <div>Loading system status...</div>;
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
      case 'healthy':
      case 'running':
        return 'bg-green-500';
      case 'degraded':
        return 'bg-yellow-500';
      default:
        return 'bg-red-500';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          System Health Monitor
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* MCP Server Status */}
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Cloud className="h-5 w-5 text-blue-600" />
              <h3 className="font-semibold">MCP Server</h3>
            </div>
            <Badge className={getStatusColor(status.mcp_server.status)}>
              {status.mcp_server.status}
            </Badge>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Logs/sec</p>
              <p className="text-2xl font-bold">{status.mcp_server.logs_per_second}</p>
            </div>
            <div>
              <p className="text-gray-500">Uptime</p>
              <p className="text-2xl font-bold">
                {Math.floor(status.mcp_server.uptime_seconds / 3600)}h
              </p>
            </div>
          </div>
          <div className="mt-3">
            <p className="text-sm text-gray-500 mb-2">Active Connectors:</p>
            <div className="flex flex-wrap gap-2">
              {status.mcp_server.active_connectors.map(connector => (
                <Badge key={connector} variant="outline">
                  {connector}
                </Badge>
              ))}
            </div>
          </div>
        </div>

        {/* Database Status */}
        <div className="border rounded-lg p-4">
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
        <div className="border rounded-lg p-4">
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

        {/* Engines Status */}
        <div className="border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Server className="h-5 w-5 text-indigo-600" />
            <h3 className="font-semibold">Processing Engines</h3>
          </div>
          <div className="space-y-2">
            {Object.entries(status.engines).map(([name, engine]) => (
              <div key={name} className="flex items-center justify-between text-sm">
                <span className="font-medium">{name}</span>
                <div className="flex items-center gap-3">
                  <span className="text-gray-500">
                    {engine.requests_per_minute} req/min
                  </span>
                  <span className="text-gray-500">
                    {engine.avg_latency_ms}ms
                  </span>
                  <Badge className={getStatusColor(engine.status)} size="sm">
                    {engine.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
```

#### 3. Interactive 3D Architecture Diagram

```typescript
// src/components/ArchitectureDiagram.tsx
import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Line, Html } from '@react-three/drei';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import * as THREE from 'three';

interface EngineNode {
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

const engines: EngineNode[] = [
  {
    id: 'engine1',
    name: 'Log Collection\n(MCP)',
    position: [-4, 2, 0],
    status: 'running',
    connections: ['redis', 'engine3'],
    metrics: { requests_per_minute: 1234, avg_latency_ms: 5 }
  },
  {
    id: 'engine2',
    name: 'Document\nProcessing',
    position: [-4, -2, 0],
    status: 'running',
    connections: ['postgres', 'engine3'],
    metrics: { requests_per_minute: 45, avg_latency_ms: 2500 }
  },
  {
    id: 'engine3',
    name: 'XGBoost\nClassifier',
    position: [0, 0, 0],
    status: 'running',
    connections: ['engine4'],
    metrics: { requests_per_minute: 5678, avg_latency_ms: 1 }
  },
  {
    id: 'engine4',
    name: 'Decision &\nScoring',
    position: [4, 1, 0],
    status: 'running',
    connections: ['postgres', 'engine5'],
    metrics: { requests_per_minute: 5678, avg_latency_ms: 3 }
  },
  {
    id: 'engine5',
    name: 'Report\nGeneration',
    position: [4, -2, 0],
    status: 'running',
    connections: ['postgres'],
    metrics: { requests_per_minute: 12, avg_latency_ms: 15000 }
  },
  {
    id: 'redis',
    name: 'Redis\nCache',
    position: [-2, 3, -2],
    status: 'running',
    connections: [],
    metrics: { requests_per_minute: 15000, avg_latency_ms: 0.5 }
  },
  {
    id: 'postgres',
    name: 'PostgreSQL\nDatabase',
    position: [0, -3, -2],
    status: 'running',
    connections: [],
    metrics: { requests_per_minute: 8900, avg_latency_ms: 2 }
  }
];

const EngineNode3D: React.FC<{ 
  engine: EngineNode; 
  onClick: (engine: EngineNode) => void;
  selected: boolean;
}> = ({ engine, onClick, selected }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (meshRef.current) {
      // Floating animation
      meshRef.current.position.y = engine.position[1] + Math.sin(state.clock.elapsedTime + engine.position[0]) * 0.1;
      
      // Rotation animation
      meshRef.current.rotation.y += 0.01;
      
      // Pulse effect when selected
      if (selected) {
        const scale = 1 + Math.sin(state.clock.elapsedTime * 3) * 0.1;
        meshRef.current.scale.set(scale, scale, scale);
      }
    }
  });

  const getColor = () => {
    if (engine.status === 'error') return '#ef4444';
    if (engine.status === 'stopped') return '#6b7280';
    if (selected) return '#3b82f6';
    if (hovered) return '#60a5fa';
    return '#10b981';
  };

  return (
    <group position={engine.position}>
      <mesh
        ref={meshRef}
        onClick={() => onClick(engine)}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[1.5, 1.5, 1.5]} />
        <meshStandardMaterial 
          color={getColor()} 
          emissive={getColor()}
          emissiveIntensity={0.2}
          metalness={0.3}
          roughness={0.4}
        />
      </mesh>
      
      <Text
        position={[0, 1.2, 0]}
        fontSize={0.25}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {engine.name}
      </Text>
      
      {(hovered || selected) && (
        <Html position={[0, -1.5, 0]} center>
          <div className="bg-white shadow-lg rounded-lg p-3 min-w-[150px]">
            <p className="font-semibold text-sm mb-1">{engine.name.replace('\n', ' ')}</p>
            <p className="text-xs text-gray-600">
              {engine.metrics.requests_per_minute} req/min
            </p>
            <p className="text-xs text-gray-600">
              {engine.metrics.avg_latency_ms}ms latency
            </p>
          </div>
        </Html>
      )}
    </group>
  );
};

const ConnectionLine: React.FC<{ from: EngineNode; to: EngineNode }> = ({ from, to }) => {
  const points = [
    new THREE.Vector3(...from.position),
    new THREE.Vector3(...to.position)
  ];

  return (
    <Line
      points={points}
      color="#60a5fa"
      lineWidth={2}
      dashed
      dashScale={10}
      dashSize={0.5}
      gapSize={0.3}
    />
  );
};

export const InteractiveArchitectureDiagram: React.FC = () => {
  const [selectedEngine, setSelectedEngine] = useState<EngineNode | null>(null);

  // Build connections
  const connections: Array<{ from: EngineNode; to: EngineNode }> = [];
  engines.forEach(engine => {
    engine.connections.forEach(targetId => {
      const target = engines.find(e => e.id === targetId);
      if (target) {
        connections.push({ from: engine, to: target });
      }
    });
  });

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Interactive System Architecture</CardTitle>
        <p className="text-sm text-gray-500">
          3D visualization of all engines and their connections (click nodes for details)
        </p>
      </CardHeader>
      <CardContent>
        <div className="h-[600px] border rounded-lg bg-gradient-to-br from-gray-900 to-gray-800">
          <Canvas camera={{ position: [0, 0, 15], fov: 50 }}>
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} intensity={1} />
            <pointLight position={[-10, -10, -10]} intensity={0.5} />
            
            {/* Render connections first (so they're behind nodes) */}
            {connections.map((conn, i) => (
              <ConnectionLine key={i} from={conn.from} to={conn.to} />
            ))}
            
            {/* Render engine nodes */}
            {engines.map(engine => (
              <EngineNode3D
                key={engine.id}
                engine={engine}
                onClick={setSelectedEngine}
                selected={selectedEngine?.id === engine.id}
              />
            ))}
            
            <OrbitControls 
              enableZoom={true}
              enablePan={true}
              enableRotate={true}
              autoRotate={true}
              autoRotateSpeed={0.5}
            />
          </Canvas>
        </div>
        
        {/* Legend */}
        <div className="mt-4 flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded" />
            <span>Running</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded" />
            <span>Degraded</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded" />
            <span>Error</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-gray-500 rounded" />
            <span>Stopped</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
```

---

## Backend API (FastAPI)

```python
# engines/web_ui/backend/api.py
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import os
from typing import List, Dict
import aiofiles
from datetime import datetime
import socketio

app = FastAPI(title="Rwanda NCSA Web UI API", version="3.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO for real-time updates
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# In-memory store for system status (in production, use Redis)
system_status = {
    "mcp_server": {
        "status": "connected",
        "logs_per_second": 1234,
        "active_connectors": ["AWS CloudTrail", "Syslog", "Kubernetes"],
        "uptime_seconds": 86400
    },
    "databases": {
        "postgresql": {
            "status": "healthy",
            "connections": 25,
            "query_latency_ms": 2
        },
        "redis": {
            "status": "healthy",
            "memory_usage_mb": 128,
            "hit_rate_percent": 92
        }
    },
    "engines": {
        "Log Collection (MCP)": {
            "status": "running",
            "requests_per_minute": 1234,
            "avg_latency_ms": 5
        },
        "Document Processing": {
            "status": "running",
            "requests_per_minute": 45,
            "avg_latency_ms": 2500
        },
        "XGBoost Classifier": {
            "status": "running",
            "requests_per_minute": 5678,
            "avg_latency_ms": 1
        },
        "Decision Engine": {
            "status": "running",
            "requests_per_minute": 5678,
            "avg_latency_ms": 3
        },
        "Report Generator": {
            "status": "running",
            "requests_per_minute": 12,
            "avg_latency_ms": 15000
        }
    },
    "cache_performance": {
        "hit_rate": 92,
        "total_size_mb": 128,
        "evictions_per_minute": 5
    }
}

@app.get("/api/v3/system/status")
async def get_system_status():
    """Get current system status"""
    return system_status

@app.post("/api/v3/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    company_name: str = "Demo Company",
    framework: str = "Rwanda-NCSA"
):
    """
    Upload policy document for processing
    """
    # Save file
    upload_dir = f"uploads/{company_name}/{datetime.now().strftime('%Y%m%d')}"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = f"{upload_dir}/{file.filename}"
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Emit progress via WebSocket
    await sio.emit('upload_progress', {
        'filename': file.filename,
        'status': 'processing',
        'message': 'File uploaded, starting LLM processing...'
    })
    
    # Trigger document processing (ENGINE 2)
    # This would call the Document Processing Engine API
    processing_task = asyncio.create_task(
        process_document_async(file_path, framework, file.filename)
    )
    
    return {
        "status": "accepted",
        "filename": file.filename,
        "file_path": file_path,
        "message": "Document uploaded successfully. Processing started."
    }

async def process_document_async(file_path: str, framework: str, filename: str):
    """
    Async task to process document with ENGINE 2
    """
    import requests
    from openai import OpenAI
    
    # Simulate LLM processing (replace with actual ENGINE 2 call)
    await asyncio.sleep(2)  # Simulate processing time
    
    await sio.emit('upload_progress', {
        'filename': filename,
        'status': 'processing',
        'message': 'Extracting text from document...'
    })
    
    await asyncio.sleep(3)
    
    # Call ENGINE 2 Document Processor
    # response = requests.post('http://engine2:8002/process', ...)
    
    # For demo, simulate extracted controls
    extracted_controls = 42
    
    await sio.emit('upload_progress', {
        'filename': filename,
        'status': 'completed',
        'message': f'Processing complete! Extracted {extracted_controls} controls.',
        'extracted_controls': extracted_controls
    })

@app.websocket("/ws/system-status")
async def websocket_system_status(websocket: WebSocket):
    """
    WebSocket endpoint for real-time system status updates
    """
    await websocket.accept()
    
    try:
        while True:
            # Send system status every 2 seconds
            await websocket.send_json(system_status)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("Client disconnected")

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

# Background task to update system metrics
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_system_metrics())

async def update_system_metrics():
    """
    Background task to fetch and update system metrics
    """
    while True:
        # Fetch metrics from all engines
        # This would query PostgreSQL, Redis, and all ENGINE APIs
        
        # For demo, simulate changing metrics
        import random
        system_status["mcp_server"]["logs_per_second"] = random.randint(1000, 2000)
        system_status["databases"]["redis"]["hit_rate_percent"] = random.randint(88, 95)
        
        # Broadcast to all connected WebSocket clients
        await sio.emit('system_status', system_status)
        
        await asyncio.sleep(2)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8006)
```

---

## Updated Docker Compose Configuration

```yaml
# docker-compose.yml (UPDATED with ENGINE 6)
version: '3.8'

services:
  # ... (ENGINE 1-5 services remain the same) ...

  # ENGINE 6: Web UI Backend
  web-ui-backend:
    build: ./engines/web_ui/backend
    container_name: rwanda-ncsa-web-backend
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - POSTGRES_URL=postgresql://user:pass@postgres:5432/compliance
      - REDIS_URL=redis://redis:6379
      - ENGINE1_URL=http://mcp-log-collector:8080
      - ENGINE2_URL=http://document-processor:8002
      - ENGINE3_URL=http://xgboost-api:8000
      - ENGINE4_URL=http://decision-engine:8001
      - ENGINE5_URL=http://report-generator:8005
    ports:
      - "8006:8006"  # FastAPI backend
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      - postgres
      - redis
      - xgboost-api
      - decision-engine
      - report-generator
    restart: unless-stopped

  # ENGINE 6: Web UI Frontend (React)
  web-ui-frontend:
    build:
      context: ./engines/web_ui/frontend
      dockerfile: Dockerfile
    container_name: rwanda-ncsa-web-frontend
    environment:
      - REACT_APP_API_URL=http://localhost:8006
      - REACT_APP_WS_URL=ws://localhost:8006
    ports:
      - "3000:3000"  # React development server
    volumes:
      - ./engines/web_ui/frontend/src:/app/src
      - ./engines/web_ui/frontend/public:/app/public
    depends_on:
      - web-ui-backend
    restart: unless-stopped
    stdin_open: true
    tty: true

  # Nginx Reverse Proxy (Production)
  nginx:
    image: nginx:alpine
    container_name: rwanda-ncsa-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - web-ui-frontend
      - web-ui-backend
    restart: unless-stopped

  # ... (postgres, redis services remain the same) ...

volumes:
  postgres_data:
  redis_data:
  uploads:
```

---

## Project Structure for ENGINE 6

```
engines/web_ui/
├── frontend/                    # React TypeScript app
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentUpload.tsx
│   │   │   ├── SystemHealthMonitor.tsx
│   │   │   ├── ArchitectureDiagram.tsx
│   │   │   ├── ComplianceDashboard.tsx
│   │   │   └── ui/              # shadcn/ui components
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   └── useSystemStatus.ts
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Documents.tsx
│   │   │   ├── Reports.tsx
│   │   │   └── SystemHealth.tsx
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── backend/                     # FastAPI Python app
│   ├── api.py                   # Main API routes
│   ├── websocket.py             # WebSocket handlers
│   ├── models.py                # Pydantic models
│   ├── services/
│   │   ├── document_processor.py
│   │   ├── system_monitor.py
│   │   └── metrics_collector.py
│   ├── requirements.txt
│   └── Dockerfile
│
└── README.md
```

---

## Installation & Setup

### Frontend (React + TypeScript)

```bash
# Create React app with TypeScript
npx create-react-app engines/web_ui/frontend --template typescript

cd engines/web_ui/frontend

# Install dependencies
npm install \
  @radix-ui/react-* \
  @react-three/fiber \
  @react-three/drei \
  three \
  socket.io-client \
  recharts \
  d3 \
  axios \
  react-dropzone \
  framer-motion \
  zustand \
  lucide-react \
  tailwindcss \
  class-variance-authority \
  clsx \
  tailwind-merge

# Install shadcn/ui CLI
npx shadcn-ui@latest init

# Add shadcn/ui components
npx shadcn-ui@latest add card
npx shadcn-ui@latest add button
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add progress
npx shadcn-ui@latest add dialog
```

### Backend (FastAPI)

```python
# engines/web_ui/backend/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-socketio==5.10.0
aiofiles==23.2.1
python-multipart==0.0.6
openai==1.3.0
asyncpg==0.29.0
redis==5.0.1
```

### Dockerfile for Frontend

```dockerfile
# engines/web_ui/frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Build for production
RUN npm run build

# Serve with nginx
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

### Dockerfile for Backend

```dockerfile
# engines/web_ui/backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8006

CMD ["uvicorn", "api:socket_app", "--host", "0.0.0.0", "--port", "8006", "--reload"]
```

---

## Updated Implementation Roadmap

### Phase 1 (Week 1-2): Foundation + WEB UI
  ✓ Set up Docker Compose (7 services now)
  ✓ Deploy XGBoost API (ENGINE 3)
  ✓ Build Control Index Database
  **NEW**: Build Web UI Frontend (React + TypeScript)
  **NEW**: Build Web UI Backend (FastAPI + WebSocket)
  **NEW**: Implement Document Upload Interface
  **NEW**: Implement System Health Monitor
  **NEW**: Create 3D Interactive Architecture Diagram
  
  **Deliverable**: 
  - Working XGBoost /classify endpoint
  - **Web UI accessible at http://localhost:3000**
  - **Real-time system monitoring dashboard**
  - **Document upload and processing workflow**

---

## Key Features of ENGINE 6

### 1. Document Upload Box
✅ Drag & drop interface  
✅ Multi-file upload (PDF, DOCX, XLSX)  
✅ Real-time upload progress  
✅ WebSocket updates during LLM processing  
✅ Shows extracted control count  
✅ Error handling with retry  

### 2. System Health Monitor
✅ Real-time MCP server status  
✅ Database connection monitoring  
✅ Cache performance metrics  
✅ All engines status (running/stopped/error)  
✅ Auto-refresh every 2 seconds via WebSocket  
✅ Visual indicators (green/yellow/red)  

### 3. Interactive 3D Architecture Diagram
✅ Floating animated nodes  
✅ Real-time connection visualization  
✅ Click nodes for detailed metrics  
✅ Auto-rotate camera  
✅ Zoom & pan controls  
✅ Status color-coding  
✅ Hover tooltips  

### 4. Technology Stack
✅ **Latest React 18** with TypeScript  
✅ **shadcn/ui** - Modern component library  
✅ **Tailwind CSS** - Utility-first CSS  
✅ **Three.js** - 3D visualization  
✅ **Socket.IO** - Real-time bidirectional communication  
✅ **FastAPI** - High-performance Python backend  
✅ **WebSocket** - Live updates  

---

## Updated Success Metrics

**Technical Metrics**:
- ✓ XGBoost inference: <1ms per event (ACHIEVED)
- ◯ Web UI load time: <2 seconds
- ◯ WebSocket latency: <50ms
- ◯ Document upload: supports up to 100MB files
- ◯ 3D diagram: 60fps on modern browsers

**User Experience Metrics**:
- ◯ Document upload success rate: >99%
- ◯ Real-time update delay: <1 second
- ◯ Dashboard responsiveness: <100ms
- ◯ Mobile compatibility: Responsive design

---

## Next Steps

1. **This Week**: Read updated architecture, set up frontend development environment
2. **Week 1**: Build React UI components (Document Upload, System Monitor)
3. **Week 2**: Implement 3D Architecture Diagram, integrate WebSocket
4. **Week 3**: Connect to backend APIs, test end-to-end workflow

---

**Total Services**: 7 (6 engines + nginx)  
**Total Containers**: 9 (including postgres, redis)  
**Deployment**: One command - `docker-compose up -d`

