import { useRef } from 'react';
import { FileUpload } from 'primereact/fileupload';
import { CheckCircle2 } from 'lucide-react';

interface ImageUploaderProps {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
}

export default function ImageUploader({ onFileSelect, selectedFile }: ImageUploaderProps) {
  const uploadRef = useRef<FileUpload>(null);

  const handleSelect = (e: { files: File[] }) => {
    if (e.files?.[0]) {
      onFileSelect(e.files[0]);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="mb-5">
      <FileUpload
        ref={uploadRef}
        mode="basic"
        name="blood_sample"
        accept="image/*"
        maxFileSize={10000000}
        auto={false}
        chooseLabel="Choose Blood Sample Image"
        onSelect={handleSelect}
        className="w-full"
      />

      {selectedFile && (
        <div className="mt-3 flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-200">
          <div className="flex items-center gap-2">
            <CheckCircle2 size={18} className="text-emerald-500" />
            <div>
              <span className="text-sm font-medium text-slate-700 block">{selectedFile.name}</span>
              <span className="text-xs text-slate-400">{formatSize(selectedFile.size)}</span>
            </div>
          </div>
          <button
            className="text-sm text-rose-600 hover:text-rose-700 font-medium"
            onClick={() => {
              onFileSelect(null);
              uploadRef.current?.clear();
            }}
          >
            Remove
          </button>
        </div>
      )}
    </div>
  );
}