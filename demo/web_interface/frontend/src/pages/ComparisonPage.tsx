import React, { useState } from 'react';
import Button from '@components/Button';
import apiService from '@services/api';

const ComparisonPage: React.FC = () => {
  const [baseline, setBaseline] = useState('LangChain');
  const [target, setTarget] = useState('LangGraph');
  const [metrics, setMetrics] = useState('response_time,memory_usage');
  const [type, setType] = useState('performance');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    setLoading(true);
    try {
      const data = await apiService.post<any>('/comparison/analyze', {
        baseline: { framework: baseline },
        target: { framework: target },
        comparison_type: type,
        metrics: metrics.split(',').map((m) => m.trim()).filter(Boolean),
      });
      setResult(data);
    } catch {} finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">对比分析</h1>
        <p className="text-gray-600 dark:text-gray-400">LangGraph vs Coze 技术对比分析</p>
      </div>

      <div className="card p-6 space-y-4">
        <div className="grid md:grid-cols-4 gap-3">
          <input className="input" value={baseline} onChange={(e) => setBaseline(e.target.value)} placeholder="baseline" />
          <input className="input" value={target} onChange={(e) => setTarget(e.target.value)} placeholder="target" />
          <input className="input" value={metrics} onChange={(e) => setMetrics(e.target.value)} placeholder="metrics" />
          <select className="input" value={type} onChange={(e) => setType(e.target.value)}>
            <option value="performance">performance</option>
            <option value="features">features</option>
            <option value="architecture">architecture</option>
            <option value="usability">usability</option>
          </select>
        </div>
        <Button onClick={analyze} disabled={loading}>开始分析</Button>

        {result && (
          <div className="grid md:grid-cols-3 gap-4">
            <div className="card p-4">
              <div className="text-sm text-gray-500">总体评分</div>
              <div className="font-semibold">{result.overall_score}</div>
            </div>
            <div className="md:col-span-2 card p-4">
              <div className="font-semibold mb-2">差异分析</div>
              <div className="space-y-1">
                {(result.differences || []).map((d: any, i: number) => (
                  <div key={i} className="text-sm">[{d.aspect}] {d.baseline} → {d.target}｜{d.improvement}</div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComparisonPage;
