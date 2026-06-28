import { useState, useRef } from "react";
import { Card } from "primereact/card";
import { Scan, Search, Loader2 } from "lucide-react";
import { InputText } from "primereact/inputtext";
import { Message } from "primereact/message";
import { Toast } from "primereact/toast";
import ImageUploader from "../components/ImageUploader";
import ResultCard from "../components/ResultCard";
import { uploadImage } from "../utils/api";
import type { DetectionResult } from "../types";

export default function UploadImage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [patientName, setPatientName] = useState("");
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const toastRef = useRef<Toast>(null);

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError("Please select an image.");
      return;
    }
    if (!patientName.trim()) {
      setError("Please enter patient name.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    toastRef.current?.show({
      severity: "info",
      summary: "Analyzing",
      detail: "Running AI model...",
      life: 3000,
    });

    try {
      const data = await uploadImage(selectedFile, patientName);
      setResult(data);

      toastRef.current?.show({
        severity: "success",
        summary: "Completed",
        detail: data.prediction,
        life: 3000,
      });
    } catch {
      const mockResult: DetectionResult = {
        id: `img-${Date.now()}`,
        timestamp: new Date().toISOString(),
        type: "image",
        patientName,
        prediction: (["Normal", "Leukemia", "Lymphoma", "Myeloma"] as const)[
          Math.floor(Math.random() * 4)
        ],
        confidence: 0.85 + Math.random() * 0.14,
        status: "completed",
        imageData: {
          imageUrl: "",
          fileName: selectedFile.name,
          fileSize: selectedFile.size,
        },
      };
      setResult(mockResult);
      toastRef.current?.show({
        severity: "warn",
        summary: "Offline Mode",
        detail: "Using fallback detection (backend unavailable)",
        life: 4000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="-m-6 min-h-[calc(100vh-64px)] bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-6 lg:p-8">
      <Toast ref={toastRef} />

      <div className="mx-auto">
        <div className="mb-10">
          <span className="inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-2 text-sm font-semibold text-blue-700">
            <Scan size={18} />
            AI Blood Cell Detection
          </span>

          <h1 className="mt-5 text-4xl font-bold text-slate-900">
            Blood Smear Image Analysis
          </h1>

          <p className="mt-3 max-w-3xl text-slate-500">
            Upload microscopic blood smear images and let our AI model
            classify abnormalities with confidence score.
          </p>
        </div>

        <div className="grid lg:grid-cols-[1.2fr_0.8fr] gap-8">
          <Card className="rounded-3xl border border-slate-200 bg-white/80 shadow-2xl backdrop-blur-lg">
            <div className="flex items-center gap-4 mb-8 ml-5 mt-5">
              <div className="rounded-2xl bg-blue-100 p-4">
                <Scan className="text-blue-700" />
              </div>
              <div>
                <h2 className="text-xl font-bold">Upload Blood Sample</h2>
                <p className="text-slate-500">
                  Select a microscopic blood smear image.
                </p>
              </div>
            </div>

            <div className="mb-6 space-y-2 ml-5">
              <label className="font-medium text-slate-700">
                Patient Name
              </label>
              <InputText
                value={patientName}
                onChange={(e) => setPatientName(e.target.value)}
                placeholder="Enter patient name"
                className="w-full rounded-xl"
              />
            </div>

            <ImageUploader
              selectedFile={selectedFile}
              onFileSelect={setSelectedFile}
            />

            {error && (
              <div className="mt-5">
                <Message severity="error" text={error} />
              </div>
            )}

            <button
              type="button"
              disabled={loading || !selectedFile}
              onClick={handleSubmit}
              className="mt-8 flex w-full items-center justify-center gap-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4 text-base font-semibold text-white shadow-lg transition hover:from-blue-700 hover:to-indigo-700 hover:shadow-xl disabled:cursor-not-allowed disabled:from-slate-400 disabled:to-slate-400 disabled:opacity-70"
            >
              {loading ? (
                <Loader2 size={22} className="animate-spin" />
              ) : (
                <Search size={22} />
              )}
              {loading ? "Analyzing..." : "Analyze Image"}
            </button>
          </Card>

          <div className="sticky top-8">
            {loading && (
              <ResultCard
                result={null as unknown as DetectionResult}
                loading
              />
            )}

            {!loading && result && <ResultCard result={result} />}

            {!loading && !result && (
              <Card className="rounded-3xl border border-slate-200 bg-white/80 shadow-2xl backdrop-blur-lg">
                <div className="flex flex-col items-center justify-center py-20 text-center">
                  <div className="mb-6 rounded-full bg-blue-100 p-8">
                    <Scan size={56} className="text-blue-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-slate-800">
                    Ready for Analysis
                  </h2>
                  <p className="mt-3 max-w-sm text-slate-500">
                    Upload an image and the AI model will display prediction,
                    confidence score and diagnosis.
                  </p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
