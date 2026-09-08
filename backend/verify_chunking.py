from pathlib import Path

from app.services.chunking import chunk_sections
from app.services.pdf_parser import extract_sections


pdf_path = Path(__file__).resolve().parents[1] / "data" / "raw_documents" / "test_file.pdf"
sections = extract_sections(str(pdf_path))
chunks = chunk_sections(sections)

assert chunks
source_metadata = {
    (section["heading"], section["page_start"], section["page_end"])
    for section in sections
}

for chunk in chunks:
    assert len(chunk["text"].split()) <= 550
    assert {"heading", "page_start", "page_end"}.issubset(chunk)
    assert (
        chunk["heading"],
        chunk["page_start"],
        chunk["page_end"],
    ) in source_metadata

print(f"TOTAL CHUNKS: {len(chunks)}")
print("STAGE 3 PASSED")
