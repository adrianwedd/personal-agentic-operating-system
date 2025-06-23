import React, { useEffect, useState } from 'react';
import ReactFlow, { Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';

const initialNodes: Node[] = [
  { id: 'plan', position: { x: 0, y: 0 }, data: { label: 'plan' } },
  { id: 'prioritise', position: { x: 150, y: 0 }, data: { label: 'prioritise' } },
  { id: 'retrieve', position: { x: 300, y: 0 }, data: { label: 'retrieve' } },
  { id: 'execute', position: { x: 450, y: 0 }, data: { label: 'execute' } },
  { id: 'respond', position: { x: 600, y: 0 }, data: { label: 'respond' } }
];

const edges: Edge[] = [
  { id: 'e1', source: 'plan', target: 'prioritise' },
  { id: 'e2', source: 'prioritise', target: 'retrieve' },
  { id: 'e3', source: 'retrieve', target: 'execute' },
  { id: 'e4', source: 'execute', target: 'respond' }
];

export default function App() {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);

  useEffect(() => {
    const es = new EventSource('/graph-events');
    es.onmessage = (evt) => {
      const data = JSON.parse(evt.data);
      setNodes((nds) =>
        nds.map((n) =>
          n.id === data.node
            ? { ...n, style: { background: data.event === 'start' ? '#fde047' : '#86efac' } }
            : n
        )
      );
    };
    return () => es.close();
  }, []);

  return (
    <div style={{ width: '100%', height: '100vh' }}>
      <ReactFlow nodes={nodes} edges={edges} fitView />
    </div>
  );
}
