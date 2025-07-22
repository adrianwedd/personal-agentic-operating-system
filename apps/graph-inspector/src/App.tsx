import React, { useEffect, useState } from 'react';
import ReactFlow, { Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';

export default function App() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    fetch('/graph-layout')
      .then((res) => res.json())
      .then((data) => {
        setNodes(data.nodes);
        setEdges(data.edges);
      });
  }, []);

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
