"use client";

import { useRef, useState } from "react";
import { FileUp, Play, X } from "lucide-react";

type UploadPanelProps = {
  isProcessing: boolean;
  onProcess: (file: File) => void;
};

export function UploadPanel({ isProcessing, onProcess }: UploadPanelProps) {
  const [file, setFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function clearFile() {
    setFile(null);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }

  return (
    <div className="border border-line bg-surface/85 p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">Invoice upload</h2>
          <p className="mt-1 text-sm text-muted">PDF only, up to 8 MB.</p>
        </div>
        <div className="flex h-11 w-11 items-center justify-center border border-line bg-surface-muted text-accent">
          <FileUp className="h-5 w-5" aria-hidden="true" />
        </div>
      </div>

      <label className="mt-5 flex cursor-pointer flex-col items-center justify-center gap-3 border border-dashed border-line bg-black/20 px-4 py-8 text-center transition hover:border-accent/70">
        <input
          ref={inputRef}
          className="sr-only"
          type="file"
          accept="application/pdf,.pdf"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
        <span className="font-medium text-foreground">
          {file ? file.name : "Choose invoice PDF"}
        </span>
        <span className="font-mono text-xs text-muted">
          {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "multipart/form-data"}
        </span>
      </label>

      <div className="mt-5 flex gap-3">
        <button
          className="inline-flex min-h-11 flex-1 items-center justify-center gap-2 bg-accent px-4 text-sm font-semibold text-black transition hover:bg-accent-strong disabled:cursor-not-allowed disabled:opacity-45"
          disabled={!file || isProcessing}
          onClick={() => file && onProcess(file)}
          type="button"
        >
          <Play className="h-4 w-4" aria-hidden="true" />
          Process
        </button>
        <button
          aria-label="Clear selected file"
          className="inline-flex min-h-11 w-11 items-center justify-center border border-line bg-surface-muted text-muted transition hover:text-foreground disabled:cursor-not-allowed disabled:opacity-45"
          disabled={!file || isProcessing}
          onClick={clearFile}
          type="button"
        >
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
