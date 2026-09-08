import app.services.entity_extraction as extraction


class FakeCollection:
    def get(self, include):
        assert include == ["documents", "metadatas"]
        return {
            "documents": [f"chunk {index}" for index in range(11)],
            "metadatas": [
                {"heading": "Architecture", "page_start": index + 1, "page_end": index + 1}
                for index in range(11)
            ],
        }


class FakeVectorStore:
    def create_or_get_collection(self, project_id):
        assert project_id == "project-1"
        return FakeCollection()


class FakeLLM:
    calls = 0

    def generate_text(self, prompt, system_prompt):
        FakeLLM.calls += 1
        assert "component_name" in system_prompt
        if FakeLLM.calls == 1:
            return '[{"component_name":"Engine","interfaces":["run"],"description":"Core engine"}]'
        return '```json\n[{"component_name":"engine","interfaces":["stop", "run"],"description":""}]\n```'


extraction.VectorStoreService = FakeVectorStore
extraction.LLMClient = FakeLLM
result = extraction.extract_entities("project-1")

assert FakeLLM.calls == 3
assert result["entities"] == [
    {
        "component_name": "Engine",
        "interfaces": ["run", "stop"],
        "description": "Core engine",
    }
]

print(f"EXTRACTED COMPONENTS: {len(result['entities'])}")
print("ENTITY EXTRACTION PASSED")
