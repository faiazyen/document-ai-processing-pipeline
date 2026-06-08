import { Braces } from "lucide-react";

export function JsonViewer({ value }: { value: unknown }) {
  return (
    <div className="border border-line bg-surface/85 p-5">
      <div className="flex items-center gap-3">
        <Braces className="h-5 w-5 text-accent" aria-hidden="true" />
        <h2 className="text-lg font-semibold">Final JSON output</h2>
      </div>
      <pre className="mt-4 max-h-[34rem] overflow-auto border border-line/70 bg-black/50 p-4 font-mono text-xs leading-5 text-slate-200">
        {JSON.stringify(value, null, 2)}
      </pre>
    </div>
  );
}
