import React, { useState } from 'react';
import Button from '@components/Button';
import apiService from '@services/api';

const VisualizationPage: React.FC = () => {
  const [sessionId, setSessionId] = useState('');
  const [depth, setDepth] = useState(3);
  const [network, setNetwork] = useState<any>(null);

  const load = async () => {
    try {
      const data = await apiService.get<any>('/memory/network', { session_id: sessionId, depth });
      setNetwork(data);
    } catch {}
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">数据可视化</h1>
        <p className="text-gray-600 dark:text-gray-400">LangGraph状态流程实时可视化</p>
      </div>

      <div className="card p-6 space-y-4">
        <div className="grid md:grid-cols-3 gap-3">
          <input className="input" placeholder="Session ID" value={sessionId} onChange={(e) => setSessionId(e.target.value)} />
          <input className="input" type="number" min={1} max={5} value={depth} onChange={(e) => setDepth(Number(e.target.value))} />
          <Button onClick={load}>加载网络</Button>
        </div>

        {network && (
          <div className="grid md:grid-cols-3 gap-4">
            <div className="card p-4">
              <div className="text-sm text-gray-500">节点数</div>
              <div className="font-semibold">{(network.nodes || []).length}</div>
            </div>
            <div className="card p-4">
              <div className="text-sm text-gray-500">边数</div>
              <div className="font-semibold">{(network.edges || []).length}</div>
            </div>
            <div className="card p-4">
              <div className="text-sm text-gray-500">中心主题</div>
              <div className="font-semibold">{network.metadata?.central_topic}</div>
            </div>
          </div>
        )}

        {network && (
          <div className="card p-4">
            <div className="font-semibold mb-3">边列表</div>
            <div className="space-y-2">
              {(network.edges || []).map((e: any, idx: number) => (
                <div key={idx} className="text-sm">{e.source} → {e.target} ({e.type})</div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VisualizationPage;
