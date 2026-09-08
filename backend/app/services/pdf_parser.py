from statistics import median

import fitz


def _page_lines(page: fitz.Page) -> list[dict]:
	lines = []
	page_dict = page.get_text("dict")

	for block in page_dict.get("blocks", []):
		if block.get("type") != 0:
			continue

		for line in block.get("lines", []):
			spans = [span for span in line.get("spans", []) if span.get("text", "").strip()]
			if not spans:
				continue

			text = " ".join(span["text"].strip() for span in spans)
			font_size = max(float(span.get("size", 0)) for span in spans)
			is_bold = any(
				span.get("flags", 0) & 16 or "bold" in span.get("font", "").lower()
				for span in spans
			)
			lines.append({"text": text, "font_size": font_size, "is_bold": is_bold})

	return lines


def _is_heading(line: dict, body_font_size: float) -> bool:
	return line["is_bold"] or line["font_size"] >= body_font_size * 1.15


def extract_sections(pdf_path: str) -> list[dict]:
	"""Extract heading-based sections from a PDF, with a page fallback."""
	sections = []

	with fitz.open(pdf_path) as document:
		page_lines = [_page_lines(page) for page in document]
		all_lines = [line for lines in page_lines for line in lines]

		if not all_lines:
			return []

		body_font_size = median(line["font_size"] for line in all_lines)
		has_headings = any(_is_heading(line, body_font_size) for line in all_lines)

		if not has_headings:
			return [
				{
					"heading": f"Page {page_number}",
					"text": document[page_number - 1].get_text("text").strip(),
					"page_start": page_number,
					"page_end": page_number,
				}
				for page_number in range(1, len(document) + 1)
			]

		current_heading = None
		current_text = []
		current_page_start = None
		current_page_end = None

		def flush_section() -> None:
			if current_heading is None:
				return
			sections.append(
				{
					"heading": current_heading,
					"text": "\n".join(current_text).strip(),
					"page_start": current_page_start,
					"page_end": current_page_end,
				}
			)

		for page_number, lines in enumerate(page_lines, start=1):
			for line in lines:
				if _is_heading(line, body_font_size):
					flush_section()
					current_heading = line["text"]
					current_text = []
					current_page_start = page_number
					current_page_end = page_number
				else:
					if current_heading is None:
						current_heading = f"Page {page_number}"
						current_text = []
						current_page_start = page_number
					current_text.append(line["text"])
					current_page_end = page_number

		flush_section()

	return sections
