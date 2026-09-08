def chunk_sections(sections: list[dict], max_tokens: int = 500) -> list[dict]:
	"""Split section text into overlapping whitespace-based chunks."""
	if max_tokens < 1:
		raise ValueError("max_tokens must be at least 1")

	overlap = min(max_tokens - 1, max(1, int(max_tokens * 0.1)))
	step = max_tokens - overlap
	chunks = []

	for section_index, section in enumerate(sections, start=1):
		words = section.get("text", "").split()
		if not words:
			word_windows = [[]]
		elif len(words) <= max_tokens:
			word_windows = [words]
		else:
			word_windows = [
				words[start : start + max_tokens]
				for start in range(0, len(words), step)
			]

		for chunk_index, window in enumerate(word_windows, start=1):
			chunks.append(
				{
					"chunk_id": f"section-{section_index}-chunk-{chunk_index}",
					"heading": section["heading"],
					"text": " ".join(window),
					"page_start": section["page_start"],
					"page_end": section["page_end"],
				}
			)

	return chunks
