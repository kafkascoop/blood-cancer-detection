import { useState, useEffect, useRef } from 'react';
import { Card } from 'primereact/card';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import { SelectButton } from 'primereact/selectbutton';
import { Tag } from 'primereact/tag';
import { Skeleton } from 'primereact/skeleton';
import {
  Settings as SettingsIcon,
  Cpu,
  Image,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Save,
} from 'lucide-react';
import { getSettings, updateSettings, getDlStatus } from '../utils/api';
import type { AppSettings, DlStatus } from '../utils/api';

const modelModeOptions = [
  {
    label: (
      <span className="flex items-center gap-2 text-sm">
        <RefreshCw size={16} />
        Auto (CNN → OpenCV)
      </span>
    ),
    value: 'auto',
  },
  {
    label: (
      <span className="flex items-center gap-2 text-sm">
        <Cpu size={16} />
        CNN Only
      </span>
    ),
    value: 'cnn',
  },
  {
    label: (
      <span className="flex items-center gap-2 text-sm">
        <Image size={16} />
        OpenCV Only
      </span>
    ),
    value: 'opencv',
  },
];

export default function Settings() {
  const toastRef = useRef<Toast>(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<AppSettings>({
    app_name: 'HematoScan',
    image_model_mode: 'auto',
  });
  const [dlStatus, setDlStatus] = useState<DlStatus | null>(null);
  const [dirty, setDirty] = useState(false);

  // --------------- Fetch settings ---------------
  useEffect(() => {
    const fetch = async () => {
      try {
        const [s, dl] = await Promise.all([getSettings(), getDlStatus()]);
        setSettings(s);
        setDlStatus(dl);
      } catch {
        toastRef.current?.show({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load settings',
          life: 3000,
        });
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  // --------------- Save ---------------
  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await updateSettings(settings);
      setSettings(updated);
      setDirty(false);
      toastRef.current?.show({
        severity: 'success',
        summary: 'Saved',
        detail: 'Settings updated successfully',
        life: 2000,
      });
    } catch {
      toastRef.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to save settings',
        life: 3000,
      });
    } finally {
      setSaving(false);
    }
  };

  // --------------- Loading skeleton ---------------
  if (loading) {
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <Skeleton width="200px" height="28px" />
        <Card>
          <div className="space-y-4">
            <Skeleton width="40%" height="20px" />
            <Skeleton width="100%" height="40px" />
            <Skeleton width="40%" height="20px" />
            <Skeleton width="100%" height="40px" />
          </div>
        </Card>
      </div>
    );
  }

  const cnnAvailable = dlStatus?.cnn_available ?? false;
  const tfAvailable = dlStatus?.tensorflow_available ?? false;
  const ptAvailable = dlStatus?.pytorch_available ?? false;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <Toast ref={toastRef} position="top-right" />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Settings</h1>
          <p className="text-sm text-gray-500 mt-1">
            Configure application behavior and model preferences
          </p>
        </div>
        <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center">
          <SettingsIcon size={22} />
        </div>
      </div>

      {/* ====================================================
          Application Name
          ==================================================== */}
      <Card className="shadow-sm border border-gray-200">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center">
            <SettingsIcon size={18} />
          </div>
          <h2 className="text-base font-semibold text-gray-800">
            Application Name
          </h2>
        </div>

        <label className="block text-xs font-medium text-gray-500 mb-1.5">
          App Name
        </label>
        <InputText
          value={settings.app_name}
          onChange={(e) => {
            setSettings((prev) => ({ ...prev, app_name: e.target.value }));
            setDirty(true);
          }}
          className="w-full max-w-sm"
          maxLength={64}
          placeholder="HematoScan"
        />
        <p className="text-xs text-gray-400 mt-1.5">
          Displayed in the sidebar brand and browser title
        </p>
      </Card>

      {/* ====================================================
          Image Model Mode
          ==================================================== */}
      <Card className="shadow-sm border border-gray-200">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center">
            <Cpu size={18} />
          </div>
          <h2 className="text-base font-semibold text-gray-800">
            Image Analysis Model
          </h2>
        </div>

        <label className="block text-xs font-medium text-gray-500 mb-2">
          Prediction Mode
        </label>
        <SelectButton
          value={settings.image_model_mode}
          onChange={(e) => {
            setSettings((prev) => ({ ...prev, image_model_mode: e.target.value }));
            setDirty(true);
          }}
          options={modelModeOptions}
          className="flex flex-wrap gap-2"
        />

        {/* Mode description */}
        <div className="mt-4 rounded-xl bg-gray-50 border border-gray-100 p-4 text-sm text-gray-600 leading-relaxed">
          {settings.image_model_mode === 'auto' && (
            <>
              <strong className="text-gray-800">Auto (Recommended):</strong>{' '}
              Tries the CNN deep learning model first. If unavailable, falls
              back to the OpenCV feature extraction + Gradient Boosting model.
              If both fail, uses a rule-based fallback.
            </>
          )}
          {settings.image_model_mode === 'cnn' && (
            <>
              <strong className="text-gray-800">CNN Only:</strong> Uses only
              the TensorFlow/Keras CNN model. Falls back directly to rule-based
              prediction if the CNN is unavailable.
            </>
          )}
          {settings.image_model_mode === 'opencv' && (
            <>
              <strong className="text-gray-800">OpenCV Only:</strong> Uses only
              the OpenCV feature extraction + Gradient Boosting model. Falls
              back directly to rule-based prediction. This is the original
              model pipeline.
            </>
          )}
        </div>

        {/* DL framework status */}
        <div className="mt-4 space-y-2">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Deep Learning Status
          </p>
          <div className="flex flex-wrap gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs">
              {tfAvailable ? (
                <CheckCircle2 size={14} className="text-emerald-500" />
              ) : (
                <AlertTriangle size={14} className="text-amber-500" />
              )}
              <span className="text-gray-600">
                TensorFlow {dlStatus?.tensorflow_version ?? '(not installed)'}
              </span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs">
              {ptAvailable ? (
                <CheckCircle2 size={14} className="text-emerald-500" />
              ) : (
                <AlertTriangle size={14} className="text-amber-500" />
              )}
              <span className="text-gray-600">
                PyTorch {dlStatus?.pytorch_version ?? '(not installed)'}
              </span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs">
              {cnnAvailable ? (
                <Tag value="Active" severity="success" rounded />
              ) : (
                <Tag value="No model" severity="warn" rounded />
              )}
              <span className="text-gray-600">CNN Model File</span>
            </div>
          </div>

          {!tfAvailable && !ptAvailable && (
            <div className="mt-2 rounded-xl border border-amber-200 bg-amber-50 p-3 flex gap-2 text-sm text-amber-700">
              <AlertTriangle size={16} className="shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">Deep learning not available</p>
                <p className="text-xs mt-0.5">
                  Install TensorFlow (requires Python &lt; 3.13) to enable CNN
                  predictions. With Python 3.14, no pre-built wheels are
                  available yet.
                </p>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* ====================================================
          Save Button
          ==================================================== */}
      <div className="flex justify-end">
        <Button
          label="Save Settings"
          icon={<Save size={16} />}
          onClick={handleSave}
          loading={saving}
          disabled={!dirty}
          className="px-6"
        />
      </div>
    </div>
  );
}
