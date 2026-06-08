import { InvoiceProcessor } from "@/components/InvoiceProcessor";

export default function Home() {
  return (
    <main className="min-h-dvh overflow-hidden bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.14),transparent_28rem),linear-gradient(180deg,#050608,#090d13_44%,#050608)]">
      <section className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-5 py-8 sm:px-8 lg:px-10">
        <header className="flex flex-col gap-6 border-b border-line/70 pb-8 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="font-mono text-xs uppercase tracking-[0.24em] text-accent">
              MaverickIQ / The Merch Maverick
            </p>
            <h1 className="mt-4 text-4xl font-semibold leading-tight text-foreground sm:text-5xl">
              Document AI Processing Pipeline
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-muted">
              Upload a B2B merchandise invoice PDF, extract structured fields,
              validate deterministic risks, and inspect the final JSON payload.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-3 text-sm">
            {["PDF text", "OpenAI JSON", "Validation"].map((label) => (
              <div
                className="border border-line bg-surface/75 px-4 py-3 text-center"
                key={label}
              >
                <div className="font-mono text-[11px] uppercase text-muted">
                  Layer
                </div>
                <div className="mt-1 font-medium text-foreground">{label}</div>
              </div>
            ))}
          </div>
        </header>
        <InvoiceProcessor />
      </section>
    </main>
  );
}
