import OpenAI from "openai";
import { zodResponseFormat } from "openai/helpers/zod";
import { invoiceExtractionPrompt } from "./invoicePrompt";
import { invoiceExtractionSchema, type InvoiceExtraction } from "./schemas";

let client: OpenAI | null = null;

function getOpenAIClient() {
  const apiKey = process.env.OPENAI_API_KEY;

  if (!apiKey) {
    throw new Error("OPENAI_API_KEY is not configured.");
  }

  if (!client) {
    client = new OpenAI({ apiKey });
  }

  return client;
}

export async function extractInvoiceWithOpenAI(
  text: string,
): Promise<InvoiceExtraction> {
  const openai = getOpenAIClient();
  const model = process.env.OPENAI_MODEL || "gpt-4.1-mini";

  const completion = await openai.chat.completions.parse({
    model,
    temperature: 0,
    messages: [
      {
        role: "system",
        content: invoiceExtractionPrompt,
      },
      {
        role: "user",
        content: `Extract the invoice schema from this PDF text:\n\n${text.slice(0, 28000)}`,
      },
    ],
    response_format: zodResponseFormat(invoiceExtractionSchema, "invoice_extraction"),
  });

  const parsed = completion.choices[0]?.message.parsed;

  if (!parsed) {
    throw new Error("OpenAI returned no structured invoice payload.");
  }

  return parsed;
}
