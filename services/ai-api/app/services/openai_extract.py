from __future__ import annotations

import json
from openai import OpenAI
from app.config import settings
from app.schemas import InvoiceExtraction, LineItem

SYSTEM_PROMPT = """You are a document AI specialist extracting structured data from B2B invoice text.
Return a JSON object matching this exact schema. Use null for unknown fields.
{
  "document_type": "invoice" or "unknown",
  "supplier_name": string or null,
  "supplier_country": string or null,
  "buyer_name": string or null,
  "invoice_number": string or null,
  "invoice_date": string (ISO 8601 preferred) or null,
  "due_date": string (ISO 8601 preferred) or null,
  "currency": string (ISO 4217, e.g. USD/EUR/GBP) or null,
  "subtotal": number or null,
  "vat_amount": number or null,
  "total_amount": number or null,
  "line_items": [{"description": string, "quantity": number, "unit_price": number, "total": number}],
  "payment_terms": string or null,
  "confidence_score": float between 0 and 1
}"""


def extract_invoice_with_openai(text: str) -> InvoiceExtraction:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract invoice data from the following text:\n\n{text[:6000]}"},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    raw = response.choices[0].message.content or "{}"
    data = json.loads(raw)

    line_items = [
        LineItem(
            description=item.get("description"),
            quantity=item.get("quantity"),
            unit_price=item.get("unit_price"),
            total=item.get("total"),
        )
        for item in data.get("line_items", [])
    ]

    return InvoiceExtraction(
        document_type=data.get("document_type", "unknown"),
        supplier_name=data.get("supplier_name"),
        supplier_country=data.get("supplier_country"),
        buyer_name=data.get("buyer_name"),
        invoice_number=data.get("invoice_number"),
        invoice_date=data.get("invoice_date"),
        due_date=data.get("due_date"),
        currency=data.get("currency"),
        subtotal=data.get("subtotal"),
        vat_amount=data.get("vat_amount"),
        total_amount=data.get("total_amount"),
        line_items=line_items,
        payment_terms=data.get("payment_terms"),
        confidence_score=float(data.get("confidence_score", 0.0)),
        extraction_source="openai",
    )
