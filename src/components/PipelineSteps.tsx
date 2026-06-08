import { Bot, CheckCircle2, FileText, GitMerge, ShieldCheck } from "lucide-react";

export type PipelineState = "idle" | "processing" | "complete" | "error";

const steps = [
  { label: "PDF text extraction", icon: FileText },
  { label: "OpenAI structured JSON", icon: Bot },
  { label: "Fallback merge", icon: GitMerge },
  { label: "Deterministic validation", icon: ShieldCheck },
];

export function PipelineSteps({
  source,
  state,
}: {
  source?: string;
  state: PipelineState;
}) {
  return (
    <div className="border border-line bg-surface/85 p-5">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Pipeline</h2>
        <span className="font-mono text-xs uppercase text-muted">
          {source?.replaceAll("_", " ") || state}
        </span>
      </div>
      <div className="mt-5 space-y-3">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const active = state === "processing" && index < 2;
          const complete = state === "complete";
          return (
            <div
              className="flex items-center gap-3 border border-line/70 bg-black/20 px-3 py-3"
              key={step.label}
            >
              <div className="flex h-9 w-9 items-center justify-center border border-line bg-surface-muted text-accent">
                {complete ? (
                  <CheckCircle2 className="h-4 w-4 text-success" aria-hidden="true" />
                ) : (
                  <Icon
                    className={active ? "h-4 w-4 animate-pulse" : "h-4 w-4"}
                    aria-hidden="true"
                  />
                )}
              </div>
              <span className="text-sm text-foreground">{step.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
