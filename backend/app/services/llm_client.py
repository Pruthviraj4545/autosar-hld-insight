from typing import Any

from app.core.config import settings


class LLMClient:
	"""Generate grounded answers with the Groq chat completions API."""

	model = "openai/gpt-oss-120b"
	max_tokens = 1000

	_system_prompt = (
		"Answer ONLY using the provided context chunks. "
		"Cite the heading and page range for every claim using the format "
		"(Section: X, p.4-5). "
		"If the context is insufficient, say exactly: "
		"I cannot find this in the provided document. Never fabricate information."
	)

	def __init__(self, client: Any | None = None, api_key: str | None = None) -> None:
		if client is None:
			from groq import Groq

			client = Groq(api_key=api_key or settings.groq_api_key)
		self.client = client

	@staticmethod
	def _format_context(context_chunks: list[dict]) -> str:
		if not context_chunks:
			return "No context chunks were retrieved."

		formatted_chunks = []
		for index, chunk in enumerate(context_chunks, start=1):
			formatted_chunks.append(
				"\n".join(
					[
						f"[Context {index}]",
						f"Section: {chunk['heading']}",
						f"Pages: p.{chunk['page_start']}-{chunk['page_end']}",
						f"Text: {chunk['text']}",
					]
				)
			)
		return "\n\n".join(formatted_chunks)

	def generate_answer(self, question: str, context_chunks: list[dict]) -> str:
		context = self._format_context(context_chunks)
		user_prompt = f"Context chunks:\n{context}\n\nQuestion:\n{question}"
		return self.generate_text(user_prompt, self._system_prompt)

	def generate_text(self, prompt: str, system_prompt: str, max_tokens: int | None = None) -> str:
		response = self.client.chat.completions.create(
			model=self.model,
			max_tokens=max_tokens or self.max_tokens,
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": prompt},
			],
		)
		return response.choices[0].message.content
