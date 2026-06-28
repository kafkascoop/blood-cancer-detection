import { useRef, useState, useEffect } from 'react';
import { Upload, X, ImageIcon, CheckCircle2 } from 'lucide-react';

interface ImageUploaderProps {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
}

export default function ImageUploader({ onFileSelect, selectedFile }: ImageUploaderProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // Cleanup blob URL on unmount
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, []);

  const handleClick = () => {
    inputRef.current?.click();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Revoke previous blob URL to avoid memory leak
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
      onFileSelect(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleRemove = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    onFileSelect(null);
    setPreviewUrl(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleChange}
        className="hidden"
      />

      {!selectedFile ? (
        <button
          type="button"
          onClick={handleClick}
          className="group w-full cursor-pointer rounded-xl border-2 border-dashed border-slate-300 bg-slate-50/50 p-8 text-center transition hover:border-blue-400 hover:bg-blue-50/30"
        >
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 transition group-hover:bg-blue-200">
            <Upload size={28} className="text-blue-600" />
          </div>
          <p className="text-base font-semibold text-slate-700">
            Choose Blood Sample Image
          </p>
          <p className="mt-1 text-sm text-slate-400">
            PNG, JPG or WEBP up to 10MB
          </p>
        </button>
      ) : (
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          {previewUrl && (
            <div className="relative mb-4 overflow-hidden rounded-lg bg-slate-100">
              <img
                src={previewUrl}
                alt={selectedFile.name}
                className="max-h-64 w-full object-contain"
              />
            </div>
          )}

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
                <ImageIcon size={20} className="text-emerald-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-700">{selectedFile.name}</p>
                <p className="text-xs text-slate-400">{formatSize(selectedFile.size)}</p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleRemove}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition hover:bg-rose-50 hover:text-rose-600"
            >
              <X size={18} />
            </button>
          </div>

          <div className="mt-3 flex items-center gap-2 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            <CheckCircle2 size={16} />
            <span>File selected — click Analyze to process</span>
          </div>
        </div>
      )}
    </div>
  );
}
