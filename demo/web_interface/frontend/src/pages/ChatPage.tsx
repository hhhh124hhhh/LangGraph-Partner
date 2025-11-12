import React, { useState } from 'react';
import Button from '@components/Button';
import LoadingSpinner from '@components/LoadingSpinner';
import apiService from '@services/api';

const ChatPage: React.FC = () => {
  const [message, setMessage] = useState('');
  const [sessionId, setSessionId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [reply, setReply] = useState<string>('');
  const [stateInfo, setStateInfo] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  const send = async () => {
    if (!message.trim()) return;
    setLoading(true);
    try {
      const res: any = await apiService.sendMessage({ message, session_id: sessionId } as any);
      setReply(res.response);
      setSessionId(res.session_id);
      const st: any = await apiService.get(`/chat/state/${res.session_id}`);
      setStateInfo(st);
      const hist: any = await apiService.get('/chat/history', { session_id: res.session_id, limit: 10, offset: 0 });
      setHistory(hist.turns || []);
    } catch (e) {
      // 错误在拦截器里提示
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">智能对话</h1>
        <p className="text-gray-600 dark:text-gray-400">与AI进行个性化对话体验</p>
      </div>

      <div className="card p-6 space-y-4">
        <div className="flex gap-3">
          <input
            className="input flex-1"
            placeholder="请输入消息..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <Button onClick={send} disabled={loading}>发送</Button>
        </div>

        {loading && (
          <div className="flex justify-center"><LoadingSpinner /></div>
        )}

        {!!reply && (
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded p-4">
            <div className="font-semibold mb-2">AI 回复</div>
            <div className="whitespace-pre-wrap">{reply}</div>
          </div>
        )}

        {stateInfo && (
          <div className="grid md:grid-cols-3 gap-4">
            <div className="card p-4">
              <div className="text-sm text-gray-500">会话ID</div>
              <div className="font-semibold break-all">{stateInfo.session_id}</div>
            </div>
            <div className="card p-4">
              <div className="text-sm text-gray-500">当前轮次</div>
              <div className="font-semibold">{stateInfo.current_turn}</div>
            </div>
            <div className="card p-4">
              <div className="text-sm text-gray-500">激活工具</div>
              <div className="font-semibold">{(stateInfo.active_tools || []).join(', ')}</div>
            </div>
          </div>
        )}

        {history.length > 0 && (
          <div className="card p-4">
            <div className="font-semibold mb-3">对话历史</div>
            <div className="space-y-3">
              {history.map((h) => (
                <div key={h.turn_id} className="border rounded p-3">
                  <div className="text-sm text-gray-500">用户</div>
                  <div className="mb-2">{h.user_message}</div>
                  <div className="text-sm text-gray-500">AI</div>
                  <div>{h.ai_response}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPage;
