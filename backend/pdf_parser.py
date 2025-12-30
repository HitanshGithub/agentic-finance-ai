from pypdf import PdfReader
import re

def parse_bank_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    expenses = []

    lines = text.split("\n")

    for line in lines:
        # Match lines like: "Rent Payment 15000"
        match = re.search(r"([A-Za-z ].+?)\s+(\d{1,3}(?:,\d{3})*)$", line)
        if match:
            description = match.group(1).strip()
            amount = int(match.group(2).replace(",", ""))

            # Ignore salary credits (heuristic)
            if "salary" in description.lower():
                continue

            expenses.append({
                "category": description,
                "amount": amount
            })

    return expenses
