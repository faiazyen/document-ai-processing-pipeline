"""
Experimental LangChain-based invoice extractor.

This module provides an alternative to the direct OpenAI SDK extraction in
app/services/openai_extract.py. It uses LangChain's structured output parsing.

WHY THIS EXISTS:
- Demonstrates awareness of the LangChain ecosystem (common GenAI Developer interview topic).
- Shows when an orchestration layer adds value vs. when direct SDK is simpler.

WHEN LANGCHAIN IS BETTER THAN DIRECT SDK:
- Multi-step reasoning chains (extract → validate → summarize → route).
- Tool use / function calling with external APIs inside the chain.
- Memory / conversation history across turns.
- Agent loops with dynamic tool selection.
- RAG pipelines with retrieval + generation in a single chain.

WHEN DIRECT SDK IS BETTER (this use case):
- Single, focused extraction call with a known JSON schema.
- Minimal dependencies and faster cold starts.
- Simpler debugging — one call, one response.
- No orchestration overhead for a deterministic extraction task.

USAGE:
    pip install langchain langchain-openai
    from app.experimental.langchain_extractor import langchain_extract_invoice

This module gracefully fails to import if langchain is not installed.
"""

from __future__ import annotations

from app.schemas import InvoiceExtraction, LineItem

LANGCHAIN_SYSTEM_PROMPT = """You are a document AI specialist extracting structured data from B2B invoice text.
Return a JSON object with these fields (use null for unknown):
document_type, supplier_name, supplier_country, buyer_name, invoice_number,
invoice_date, due_date, currency, subtotal, vat_amount, total_amount,
line_items (list of {description, quantity, unit_price, total}),
payment_terms, confidence_score (0-1 float)."""


def langchain_extract_invoice(text: str, model: str = "gpt-4.1-mini") -> InvoiceExtraction:
    """
    Extract invoice fields using LangChain's chat model with JSON output parsing.

    Raises ImportError if langchain or langchain-openai are not installed.
    Raises ValueError if OPENAI_API_KEY is not set.
    """
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_core.output_parsers import JsonOutputParser
    except ImportError as exc:
        raise ImportError(
            "langchain and langchain-openai are required for the experimental extractor. "
            "Install with: pip install langchain langchain-openai"
        ) from exc

    from app.config import settings

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for LangChain extraction.")

    llm = ChatOpenAI(
        model=model,
        temperature=0,
        api_key=settings.openai_api_key,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    messages = [
        SystemMessage(content=LANGCHAIN_SYSTEM_PROMPT),
        HumanMessage(content=f"Extract invoice data from:\n\n{text[:6000]}"),
    ]

    parser = JsonOutputParser()
    chain = llm | parser
    data: dict = chain.invoke(messages)

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
        extraction_source="openai",  # same model, different orchestration layer
    )
