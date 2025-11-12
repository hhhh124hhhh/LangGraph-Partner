import React, { useEffect, useState } from 'react';
import Button from '@components/Button';
import apiService from '@services/api';

const SettingsPage: React.FC = () => {
  const [context, setContext] = useState<any>(null);
  const [form, setForm] = useState<any>({ name: '', role: '', expertise_areas: [] });
  const [validate, setValidate] = useState<any>(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await apiService.get<any>('/persona/context');
        setContext(data);
        setForm({ name: data?.user_persona?.name || '', role: data?.user_persona?.role || '', expertise_areas: data?.user_persona?.expertise_areas || [] });
      } catch {}
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

  return (
    <div className="space-y-6">
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
    </div>
  );
};

export default SettingsPage;
