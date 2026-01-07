import { useState, useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// Step definitions
const allSteps = [
  { id: '1', label: 'Write PRD/Spec', description: 'Define what you want to build', phase: 'setup' },
  { id: '2', label: 'Generate feature_list.json', description: 'Break into small features', phase: 'setup' },
  { id: '3', label: 'Start Loop', description: 'Begin the deterministic process', phase: 'setup' },
  { id: '4', label: 'Get Next Feature', description: 'python3 features.py get-next', phase: 'loop' },
  { id: '5', label: 'Implement Feature', description: 'Write code, run tests', phase: 'loop' },
  { id: '6', label: 'Mark Complete', description: 'python3 features.py mark-complete', phase: 'loop' },
  { id: '7', label: 'Update Learnings', description: 'Save patterns discovered', phase: 'loop' },
  { id: '8', label: 'Git Commit', description: 'Commit with feature description', phase: 'loop' },
  { id: '9', label: 'More Features?', description: 'Check if pending features remain', phase: 'decision' },
  { id: '10', label: 'Done!', description: 'All features complete', phase: 'complete' },
];

// Note nodes
const noteNodes = [
  {
    id: 'note-json',
    content: `{
  "description": "Add logout button",
  "steps": ["Create component", "Add handler"],
  "passes": false
}`,
    appearsWithStep: 4,
    position: { x: 450, y: 80 },
  },
  {
    id: 'note-learnings',
    content: 'Updates project_profile.json\nwith patterns discovered',
    appearsWithStep: 7,
    position: { x: 450, y: 320 },
  },
];

// Edge connections
const edgeConnections = [
  { source: '1', target: '2', sourceHandle: 'bottom', targetHandle: 'top' },
  { source: '2', target: '3', sourceHandle: 'bottom', targetHandle: 'top' },
  { source: '3', target: '4', sourceHandle: 'bottom', targetHandle: 'top' },
  { source: '4', target: '5', sourceHandle: 'bottom', targetHandle: 'top' },
  { source: '5', target: '6', sourceHandle: 'bottom', targetHandle: 'top' },
  { source: '6', target: '7', sourceHandle: 'bottom', targetHandle: 'top' },
  { source: '7', target: '8', sourceHandle: 'bottom', targetHandle: 'top' },
  { source: '8', target: '9', sourceHandle: 'bottom', targetHandle: 'top' },
  { source: '9', target: '4', sourceHandle: 'left', targetHandle: 'left', label: 'Yes' },
  { source: '9', target: '10', sourceHandle: 'bottom', targetHandle: 'top', label: 'No' },
];

// Phase colors
const phaseColors: Record<string, { bg: string; border: string }> = {
  setup: { bg: '#fef3c7', border: '#f59e0b' },
  loop: { bg: '#dbeafe', border: '#3b82f6' },
  decision: { bg: '#fef3c7', border: '#f59e0b' },
  complete: { bg: '#d1fae5', border: '#10b981' },
};

function createNode(step: typeof allSteps[0], index: number): Node {
  const colors = phaseColors[step.phase];
  const isDecision = step.phase === 'decision';

  // Position calculation
  let x = 200;
  let y = index * 80;

  // Loop nodes are offset
  if (step.phase === 'loop') {
    y = 240 + (index - 3) * 70;
  } else if (step.phase === 'decision') {
    y = 590;
  } else if (step.phase === 'complete') {
    y = 680;
  }

  return {
    id: step.id,
    position: { x, y },
    data: {
      label: (
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{step.label}</div>
          <div style={{ fontSize: '11px', color: '#666', marginTop: '4px' }}>{step.description}</div>
        </div>
      )
    },
    style: {
      background: colors.bg,
      border: `2px solid ${colors.border}`,
      borderRadius: isDecision ? '50%' : '8px',
      padding: '10px 15px',
      width: isDecision ? 120 : 200,
      height: isDecision ? 120 : 'auto',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    },
  };
}

function createNoteNode(note: typeof noteNodes[0]): Node {
  return {
    id: note.id,
    position: note.position,
    data: {
      label: (
        <pre style={{
          margin: 0,
          fontSize: '10px',
          fontFamily: 'monospace',
          whiteSpace: 'pre-wrap',
          textAlign: 'left',
        }}>
          {note.content}
        </pre>
      ),
    },
    style: {
      background: '#f8fafc',
      border: '1px dashed #94a3b8',
      borderRadius: '4px',
      padding: '8px',
      maxWidth: '200px',
    },
  };
}

export default function App() {
  const [visibleCount, setVisibleCount] = useState(1);

  const visibleNodes = useMemo(() => {
    const stepNodes = allSteps
      .slice(0, visibleCount)
      .map((step, i) => createNode(step, i));

    const visibleNotes = noteNodes
      .filter(note => note.appearsWithStep <= visibleCount)
      .map(note => createNoteNode(note));

    return [...stepNodes, ...visibleNotes];
  }, [visibleCount]);

  const visibleEdges = useMemo(() => {
    return edgeConnections
      .filter(edge => {
        const sourceIdx = allSteps.findIndex(s => s.id === edge.source);
        const targetIdx = allSteps.findIndex(s => s.id === edge.target);
        return sourceIdx < visibleCount && targetIdx < visibleCount;
      })
      .map(edge => ({
        id: `${edge.source}-${edge.target}`,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.sourceHandle,
        targetHandle: edge.targetHandle,
        label: edge.label,
        type: 'smoothstep',
        animated: edge.label === 'Yes',
        style: { stroke: edge.label === 'Yes' ? '#3b82f6' : '#94a3b8' },
      }));
  }, [visibleCount]);

  const handleNext = () => setVisibleCount(c => Math.min(c + 1, allSteps.length));
  const handlePrev = () => setVisibleCount(c => Math.max(c - 1, 1));
  const handleReset = () => setVisibleCount(1);

  return (
    <div style={{ width: '100vw', height: '100vh', fontFamily: 'system-ui' }}>
      <div style={{
        textAlign: 'center',
        padding: '20px',
        borderBottom: '1px solid #e5e7eb',
      }}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>How Project Builder Works</h1>
        <p style={{ margin: '8px 0 0', color: '#666' }}>
          Deterministic AI agent loop for building projects
        </p>
      </div>

      <div style={{ height: 'calc(100vh - 180px)' }}>
        <ReactFlow
          nodes={visibleNodes}
          edges={visibleEdges}
          fitView
          attributionPosition="bottom-left"
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>

      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '16px',
        padding: '20px',
        borderTop: '1px solid #e5e7eb',
      }}>
        <button
          onClick={handlePrev}
          disabled={visibleCount <= 1}
          style={{
            padding: '8px 24px',
            fontSize: '14px',
            cursor: visibleCount <= 1 ? 'not-allowed' : 'pointer',
            opacity: visibleCount <= 1 ? 0.5 : 1,
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            background: 'white',
          }}
        >
          Previous
        </button>
        <span style={{ padding: '8px', color: '#666' }}>
          Step {visibleCount} of {allSteps.length}
        </span>
        <button
          onClick={handleNext}
          disabled={visibleCount >= allSteps.length}
          style={{
            padding: '8px 24px',
            fontSize: '14px',
            cursor: visibleCount >= allSteps.length ? 'not-allowed' : 'pointer',
            opacity: visibleCount >= allSteps.length ? 0.5 : 1,
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            background: 'white',
          }}
        >
          Next
        </button>
        <button
          onClick={handleReset}
          style={{
            padding: '8px 24px',
            fontSize: '14px',
            cursor: 'pointer',
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            background: 'white',
          }}
        >
          Reset
        </button>
      </div>

      <div style={{ textAlign: 'center', padding: '8px', color: '#999', fontSize: '12px' }}>
        Click Next to reveal each step
      </div>
    </div>
  );
}
