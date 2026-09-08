from pathlib import Path

from app.services.pdf_parser import extract_sections


pdf_path = Path(__file__).resolve().parents[1] / "data" / "raw_documents" / "test_file.pdf"
sections = extract_sections(str(pdf_path))

assert isinstance(sections, list) and sections
for section in sections:
    assert {"heading", "text", "page_start", "page_end"}.issubset(section)

print(sections[0])
print("STAGE 2 PASSED")
