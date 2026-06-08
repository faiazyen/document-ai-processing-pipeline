import { AlertTriangle, CheckCircle2 } from "lucide-react";
import type { ValidationWarning } from "@/lib/schemas";

export function ValidationPanel({ warnings }: { warnings: ValidationWarning[] }) {
  return (
    <div className="border border-line bg-surface/85 p-5">
      <div className="flex items-center gap-3">
        {warnings.length > 0 ? (
          <AlertTriangle className="h-5 w-5 text-warning" aria-hidden="true" />
        ) : (
          <CheckCircle2 className="h-5 w-5 text-success" aria-hidden="true" />
        )}
        <h2 className="text-lg font-semibold">Validation warnings</h2>
      </div>

      <div className="mt-4 space-y-3">
        {warnings.length === 0 ? (
          <p className="border border-line/70 bg-black/20 p-3 text-sm text-muted">
            No deterministic validation warnings.
          </p>
        ) : (
          warnings.map((warning) => (
            <div className="border border-line/70 bg-black/20 p-3" key={warning.code}>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs uppercase text-warning">
                  {warning.severity}
                </span>
                <span className="font-mono text-xs text-muted">{warning.code}</span>
              </div>
              <p className="mt-1 text-sm text-foreground">{warning.message}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
