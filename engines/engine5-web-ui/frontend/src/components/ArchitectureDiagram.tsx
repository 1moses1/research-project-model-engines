import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Line, Html } from '@react-three/drei';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { EngineNode } from '@/types';
import * as THREE from 'three';

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

interface EngineNode3DProps {
  engine: EngineNode;
  onClick: (engine: EngineNode) => void;
  selected: boolean;
}

const EngineNode3D: React.FC<EngineNode3DProps> = ({ engine, onClick, selected }) => {
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
      } else {
        meshRef.current.scale.set(1, 1, 1);
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
          <div className="bg-white shadow-lg rounded-lg p-3 min-w-[150px] border border-gray-200">
            <p className="font-semibold text-sm mb-1">{engine.name.replace('\n', ' ')}</p>
            <p className="text-xs text-gray-600">
              {engine.metrics.requests_per_minute.toLocaleString()} req/min
            </p>
            <p className="text-xs text-gray-600">
              {engine.metrics.avg_latency_ms}ms latency
            </p>
            <p className="text-xs font-medium mt-1">
              <span className={`inline-block w-2 h-2 rounded-full mr-1 ${
                engine.status === 'running' ? 'bg-green-500' : 'bg-red-500'
              }`} />
              {engine.status}
            </p>
          </div>
        </Html>
      )}
    </group>
  );
};

interface ConnectionLineProps {
  from: EngineNode;
  to: EngineNode;
}

const ConnectionLine: React.FC<ConnectionLineProps> = ({ from, to }) => {
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
        <p className="text-sm text-muted-foreground">
          3D visualization of all engines and their connections (click nodes for details)
        </p>
      </CardHeader>
      <CardContent>
        <div className="h-[600px] border rounded-lg bg-gradient-to-br from-gray-900 to-gray-800 overflow-hidden">
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
          <div className="ml-auto text-xs text-gray-500">
            Drag to rotate • Scroll to zoom • Click nodes for details
          </div>
        </div>

        {/* Selected Engine Details */}
        {selectedEngine && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-semibold mb-2">{selectedEngine.name.replace('\n', ' ')}</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Requests/min</p>
                <p className="text-lg font-bold">
                  {selectedEngine.metrics.requests_per_minute.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-gray-600">Avg Latency</p>
                <p className="text-lg font-bold">
                  {selectedEngine.metrics.avg_latency_ms}ms
                </p>
              </div>
              <div>
                <p className="text-gray-600">Status</p>
                <p className="text-lg font-bold capitalize">
                  {selectedEngine.status}
                </p>
              </div>
              <div>
                <p className="text-gray-600">Connections</p>
                <p className="text-lg font-bold">
                  {selectedEngine.connections.length}
                </p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
