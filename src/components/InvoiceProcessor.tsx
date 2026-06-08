"use client";

import { useMemo, useState } from "react";
import { AlertCircle, FileJson, Loader2 } from "lucide-react";
import { ExtractionResult } from "./ExtractionResult";
import { JsonViewer } from "./JsonViewer";
import { PipelineSteps, type PipelineState } from "./PipelineSteps";
import { UploadPanel } from "./UploadPanel";
import { ValidationPanel } from "./ValidationPanel";
import type { InvoiceErrorResponse, InvoiceProcessResponse } from "@/lib/schemas";

type RequestState = "idle" | "processing" | "success" | "error";

export function InvoiceProcessor() {
  const [state, setState] = useState<RequestState>("idle");
  const [result, setResult] = useState<InvoiceProcessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const pipelineState: PipelineState = useMemo(() => {
    if (state === "processing") return "processing";
    if (state === "success") return "complete";
    if (state === "error") return "error";
    return "idle";
  }, [state]);

  async function processFile(file: File) {
    setState("processing");
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/process-invoice", {
        method: "POST",
        body: formData,
      });
      const payload = (await response.json()) as
        | InvoiceProcessResponse
        | InvoiceErrorResponse;

      if (!payload.success) {
        throw new Error(payload.error || "Invoice processing failed.");
      }

      if (!response.ok) {
        throw new Error("Invoice processing failed.");
      }

      setResult(payload);
      setState("success");
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Invoice processing failed.",
      );
      setState("error");
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(280px,0.85fr)_minmax(0,1.35fr)]">
      <aside className="flex flex-col gap-6">
        <UploadPanel isProcessing={state === "processing"} onProcess={processFile} />
        <PipelineSteps source={result?.extraction_source} state={pipelineState} />
      </aside>
      <section className="flex min-w-0 flex-col gap-6">
        {state === "processing" && (
          <StatusPanel
            icon={<Loader2 className="h-5 w-5 animate-spin" />}
            title="Processing invoice"
            text="Extracting PDF text, running structured extraction, and validating totals."
          />
        )}
        {state === "error" && (
          <StatusPanel
            icon={<AlertCircle className="h-5 w-5" />}
            tone="error"
            title="Processing failed"
            text={error || "Unknown processing error."}
          />
        )}
        {!result && state === "idle" && (
          <StatusPanel
            icon={<FileJson className="h-5 w-5" />}
            title="Awaiting invoice"
            text="The pipeline returns structured invoice fields, confidence, warnings, and raw JSON."
          />
        )}
        {result && (
          <>
            <ExtractionResult result={result} />
            <ValidationPanel warnings={result.validation_warnings} />
            <JsonViewer value={result} />
          </>
        )}
      </section>
    </div>
  );
}

function StatusPanel({
  icon,
  text,
  title,
  tone = "default",
}: {
  icon: React.ReactNode;
  text: string;
  title: string;
  tone?: "default" | "error";
}) {
  return (
    <div className="border border-line bg-surface/85 p-6">
      <div
        className={
          tone === "error"
            ? "flex items-center gap-3 text-danger"
            : "flex items-center gap-3 text-accent"
        }
      >
        {icon}
        <h2 className="text-lg font-semibold text-foreground">{title}</h2>
      </div>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">{text}</p>
    </div>
  );
}
