"""Generate two small text-based PDF invoices for seeding the demo API.

Uses fpdf2 (installed into the service venv for tooling only, not a runtime dep).
"""
from fpdf import FPDF

INVOICES = [
    {
        "filename": "invoice-acme-textiles-1042.pdf",
        "lines": [
            "INVOICE",
            "",
            "Invoice Number: INV-1042",
            "Invoice Date: 2026-08-12",
            "Due Date: 2026-09-11",
            "",
            "Supplier: Acme Textiles GmbH",
            "Supplier Country: Germany",
            "Bill To: Atlas Retail Group Ltd",
            "",
            "Description                      Qty    Unit Price    Total",
            "Custom polo shirts, embroidered  120    14.50         1740.00",
            "Setup fee, embroidery digitizing   1    45.00           45.00",
            "",
            "Subtotal: 1785.00 EUR",
            "VAT (19%): 339.15 EUR",
            "TOTAL: 2124.15 EUR",
            "",
            "Payment Terms: Net 30",
        ],
    },
    {
        "filename": "invoice-nordic-print-577.pdf",
        "lines": [
            "INVOICE",
            "",
            "Invoice Number: NP-577",
            "Invoice Date: 2026-08-20",
            "Due Date: 2026-09-04",
            "",
            "Supplier: Nordic Print Co AB",
            "Supplier Country: Sweden",
            "Bill To: Harbor Hotels Group",
            "",
            "Description                      Qty    Unit Price    Total",
            "Branded tote bags, 2-color print 300     3.20         960.00",
            "Rush production surcharge          1    75.00          75.00",
            "",
            "Subtotal: 1035.00 EUR",
            "VAT (25%): 258.75 EUR",
            "TOTAL: 1293.75 EUR",
            "",
            "Payment Terms: Net 15",
        ],
    },
]

for spec in INVOICES:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=11)
    for line in spec["lines"]:
        pdf.cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(spec["filename"])
    print(f"wrote {spec['filename']}")
