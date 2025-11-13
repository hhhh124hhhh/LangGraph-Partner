import React, { useEffect, useState } from 'react';
import Button from '@components/Button';
import apiService from '@services/api';

const SettingsPage: React.FC = () => {
  const [context, setContext] = useState<any>(null);
  const [form, setForm] = useState<any>({ name: '', role: '', expertise_areas: [] });
  const [validate, setValidate] = useState<any>(null);
  const [model, setModel] = useState<string>('');
  const [modelLoading, setModelLoading] = useState<boolean>(false);
  const [apiKey, setApiKey] = useState<string>('');
  const [baseUrl, setBaseUrl] = useState<string>('');
  const [configLoading, setConfigLoading] = useState<boolean>(false);
  const [modelOptions, setModelOptions] = useState<string[]>([]);
  const [validateLoading, setValidateLoading] = useState<boolean>(false);
  const [notification, setNotification] = useState<{ type: "success" | "error" | "info", message: string } | null>(null);
  const [configSources, setConfigSources] = useState<any>(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await apiService.get<any>('/persona/context');
        setContext(data);
        setForm({ name: data?.user_persona?.name || '', role: data?.user_persona?.role || '', expertise_areas: data?.user_persona?.expertise_areas || [] });
      } catch {}
      try {
        setModelLoading(true);
        const cfg = await apiService.getSettingsConfig();
        setModel(cfg.model || '');
        setApiKey(cfg.api_key || '');
        setBaseUrl(cfg.base_url || '');
        const v = await apiService.validateSettings({ api_key: cfg.api_key, base_url: cfg.base_url });
        setModelOptions(v.models || []);
        if (!cfg.model && v.models?.length) setModel(v.models[0]);
      } catch {}
      finally { setModelLoading(false); }
    })();
  }, []);

  const update = async () => {
    try {
      await apiService.post<any>('/persona/update', { persona_type: 'user', attributes: form, merge_strategy: 'merge' });
      const data = await apiService.get<any>('/persona/context');
      setContext(data);
    } catch {}
  };

  const doValidate = async () => {
    try {
      const data = await apiService.post<any>('/persona/validate?persona_type=user', form);
      setValidate(data);
    } catch {}
  };

  const saveModel = async () => {
    try {
      setModelLoading(true);
      const updated = await apiService.setSettingsConfig({ model });
      setModel(updated.model || model);
    } catch {}
    finally { setModelLoading(false); }
  };

  const saveConfig = async () => {
    try {
      setConfigLoading(true);
      const updated = await apiService.setSettingsConfig({ api_key: apiKey, base_url: baseUrl, model });
      setApiKey(updated.api_key || apiKey);
      setBaseUrl(updated.base_url || baseUrl);
      setModel(updated.model || model);
      const v = await apiService.validateSettings({ api_key: updated.api_key, base_url: updated.base_url });
      setModelOptions(v.models || modelOptions);
    } catch {}
    finally { setConfigLoading(false); }
  };
const validateAndFetchModels = async () => {    try {      setValidateLoading(true);            if (!apiKey || !baseUrl) {        showNotification("error", "请先填写 API Key 和基础 URL");        return;      }            showNotification("info", "正在验证接口配置并获取模型列表...");      const v = await apiService.validateSettings({ api_key: apiKey, base_url: baseUrl });            if (v.valid && v.models?.length > 0) {        setModelOptions(v.models);        if (!model) {          setModel(v.models[0]);        }        showNotification("success", `接口验证成功！获取到 ${v.models.length} 个可用模型`);      } else {        showNotification("error", "接口验证失败，请检查 API Key 和基础 URL 是否正确");      }    } catch (error: any) {      console.error("验证失败:", error);      showNotification("error", `验证失败: ${error.message || "网络错误，请稍后重试"}`);    } finally {      setValidateLoading(false);    }  };

  const showNotification = (type: "success" | "error" | "info", message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 3000);
  };

  return (
    <div className="space-y-6">
      {/* 通知显示 */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm ${          notification.type === "success" ? "bg-green-500 text-white" :
          notification.type === "error" ? "bg-red-500 text-white" :
          "bg-blue-500 text-white"
        }`}>
          <div className="flex items-center justify-between">
            <span>{notification.message}</span>
            <button
              onClick={() => setNotification(null)}
              className="ml-4 text-white hover:text-gray-200"
            >
              ✕
            </button>
          </div>
        </div>
      )}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">系统设置</h1>
        <p className="text-gray-600 dark:text-gray-400">配置系统参数和用户偏好</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="card p-6 space-y-4">
          <div className="font-semibold">画像编辑</div>
          <input className="input" placeholder="姓名" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input className="input" placeholder="角色" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
          <input className="input" placeholder="专业领域（逗号分隔）" value={(form.expertise_areas || []).join(',')} onChange={(e) => setForm({ ...form, expertise_areas: e.target.value.split(',').map((v) => v.trim()).filter(Boolean) })} />
          <div className="flex gap-3">
            <Button onClick={update}>更新画像</Button>
            <Button variant="outline" onClick={doValidate}>验证画像</Button>
          </div>
          
          {/* 环境配置状态提示 */}
          {configSources && (configSources.api_key === "env" || configSources.base_url === "env") && (
            <div className="card p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
              <div className="flex items-center gap-3">
                <span className="text-2xl">📁</span>
                <div>
                  <div className="font-medium text-blue-800 dark:text-blue-200">环境变量配置已加载</div>
                  <div className="text-sm text-blue-600 dark:text-blue-400">测试阶段自动从 .env 文件读取配置，无需手动输入</div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="card p-6 space-y-3">
          <div className="font-semibold">画像上下文</div>
          {context ? (
            <div className="text-sm whitespace-pre-wrap">
              用户：{context.user_persona?.name}（{context.user_persona?.role}）
            </div>
          ) : (
            <div className="text-sm text-gray-500">加载中或暂无数据</div>
          )}

          {validate && (
            <div className="mt-4">
              <div className="font-semibold">验证结果</div>
              <div className="text-sm">完整度：{validate.completeness_score}</div>
              <div className="text-sm">缺失字段：{(validate.missing_fields || []).join(', ')}</div>
            </div>
          )}
        </div>
      </div>

      <div className="card p-6 space-y-4">
        <div className="font-semibold">接口与基础配置</div>
        <div className="flex items-center gap-3">
          <div className="w-24 text-sm text-gray-600 dark:text-gray-400">api-key</div>
          <input className="input flex-1" placeholder="API密钥" type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} />
        </div>
        {configSources?.api_key === "env" && (
          <div className="text-sm text-green-600 dark:text-green-400 flex items-center gap-2">
            <span>📁</span>
            <span>API Key来源：环境变量文件 (已遮掩显示)</span>
          </div>
        )}
        <div className="flex items-center gap-3">
          <div className="w-24 text-sm text-gray-600 dark:text-gray-400">基础URL地址</div>
          <input className="input flex-1" placeholder="基础URL" value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} />
        </div>
        {configSources?.base_url === "env" && (
          <div className="text-sm text-green-600 dark:text-green-400 flex items-center gap-2">
            <span>📁</span>
            <span>配置来源：环境变量文件 (.env)</span>
          </div>
        )}
        <div className="flex items-center gap-3">
          <Button onClick={saveConfig} disabled={configLoading}>保存配置</Button>
          {configLoading && <span className="text-sm text-gray-500">保存中...</span>}
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-400">当前基础URL：{baseUrl || '未设置'}</div>
      </div>

      <div className="card p-6 space-y-4">
        <div className="font-semibold">模型设置（与环境变量一致）</div>
        <div className="flex items-center gap-3">
          <select className="input" value={model} onChange={(e) => setModel(e.target.value)}>
            <option value="">选择模型</option>
            {modelOptions.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
          <Button onClick={saveModel} disabled={modelLoading || !model}>保存</Button>
          {modelLoading && <span className="text-sm text-gray-500">保存中...</span>}
          <Button variant="outline" onClick={validateAndFetchModels} disabled={validateLoading}>校验并拉取模型</Button>
          {validateLoading && <span className="text-sm text-gray-500">校验中...</span>}
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-400">当前模型：{model || '未设置'}</div>
      </div>
    </div>
  );
};

export default SettingsPage;
