import { processInvoiceFile } from "@/lib/processInvoice";
import type { InvoiceErrorResponse } from "@/lib/schemas";

export const runtime = "nodejs";
export const maxDuration = 60;

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");

    if (!(file instanceof File)) {
      return Response.json(
        {
          success: false,
          error: "Request must include a PDF file field named `file`.",
          validation_warnings: [],
        } satisfies InvoiceErrorResponse,
        { status: 400 },
      );
    }

    const result = await processInvoiceFile(file);
    return Response.json(result);
  } catch (error) {
    return Response.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Invoice processing failed.",
        validation_warnings: [],
      } satisfies InvoiceErrorResponse,
      { status: 400 },
    );
  }
}
