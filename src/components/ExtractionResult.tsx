import { Gauge, ReceiptText } from "lucide-react";
import type { InvoiceProcessResponse } from "@/lib/schemas";

const fieldLabels: Array<[keyof InvoiceProcessResponse["extraction"], string]> = [
  ["supplier_name", "Supplier"],
  ["buyer_name", "Buyer"],
  ["invoice_number", "Invoice no."],
  ["invoice_date", "Invoice date"],
  ["due_date", "Due date"],
  ["currency", "Currency"],
  ["subtotal", "Subtotal"],
  ["vat_amount", "VAT / tax"],
  ["total_amount", "Total"],
];

export function ExtractionResult({ result }: { result: InvoiceProcessResponse }) {
  const confidence = Math.round(result.confidence_score * 100);

  return (
    <div className="border border-line bg-surface/85 p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <ReceiptText className="h-5 w-5 text-accent" aria-hidden="true" />
          <h2 className="text-lg font-semibold">Structured extraction</h2>
        </div>
        <div className="flex items-center gap-2 font-mono text-sm text-accent">
          <Gauge className="h-4 w-4" aria-hidden="true" />
          {confidence}% confidence
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {fieldLabels.map(([key, label]) => (
          <div className="border border-line/70 bg-black/20 p-3" key={String(key)}>
            <div className="font-mono text-[11px] uppercase text-muted">{label}</div>
            <div className="mt-1 min-h-6 break-words text-sm font-medium text-foreground">
              {formatValue(result.extraction[key])}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-5 overflow-hidden border border-line/70">
        <table className="w-full border-collapse text-left text-sm">
          <thead className="bg-surface-muted text-xs uppercase text-muted">
            <tr>
              <th className="px-3 py-2 font-medium">Description</th>
              <th className="px-3 py-2 font-medium">Qty</th>
              <th className="px-3 py-2 font-medium">Unit</th>
              <th className="px-3 py-2 font-medium">Total</th>
            </tr>
          </thead>
          <tbody>
            {result.extraction.line_items.length === 0 ? (
              <tr>
                <td className="px-3 py-4 text-muted" colSpan={4}>
                  No line items extracted.
                </td>
              </tr>
            ) : (
              result.extraction.line_items.map((item, index) => (
                <tr className="border-t border-line/70" key={`${item.description}-${index}`}>
                  <td className="px-3 py-2">{item.description || "Unknown item"}</td>
                  <td className="px-3 py-2 font-mono">{formatValue(item.quantity)}</td>
                  <td className="px-3 py-2 font-mono">{formatValue(item.unit_price)}</td>
                  <td className="px-3 py-2 font-mono">{formatValue(item.total)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "Not found";
  }

  if (typeof value === "number") {
    return value.toLocaleString("en-US", { maximumFractionDigits: 2 });
  }

  return String(value);
}
