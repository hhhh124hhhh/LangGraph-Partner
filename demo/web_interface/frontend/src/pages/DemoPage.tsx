import React, { useEffect, useState } from 'react';
import Button from '@components/Button';
import apiService from '@services/api';

const DemoPage: React.FC = () => {
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await apiService.get<any[]>('/demo/scenarios');
        setScenarios(data);
      } catch {}
    })();
  }, []);

  const run = async (id: string) => {
    setRunning(true);
    try {
      const data = await apiService.post<any>(`/demo/run/${id}`, { interactive_mode: true });
      setResult(data);
    } catch {} finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">功能演示</h1>
        <p className="text-gray-600 dark:text-gray-400">体验AI Partner的核心功能特性</p>
      </div>

      <div className="grid grid-responsive">
        {scenarios.map((s) => (
          <div key={s.scenario_id} className="card p-6 space-y-2">
            <div className="text-xl font-semibold">{s.name}</div>
            <div className="text-gray-600 dark:text-gray-400">{s.description}</div>
            <div className="text-sm text-gray-500">分类：{s.category}｜难度：{s.difficulty}</div>
            <Button onClick={() => run(s.scenario_id)} disabled={running}>运行</Button>
          </div>
        ))}
      </div>

      {result && (
        <div className="card p-6 space-y-2">
          <div className="font-semibold">运行结果</div>
          <div className="text-sm text-gray-500">Run ID: {result.run_id}</div>
          <div className="space-y-1">
            {(result.result?.outputs || []).map((o: string, i: number) => (
              <div key={i}>{o}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DemoPage;
