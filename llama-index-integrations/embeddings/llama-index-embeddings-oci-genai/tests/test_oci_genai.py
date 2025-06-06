"""Test OCI Generative AI embedding service."""

from unittest.mock import MagicMock
from typing import Any

import pytest
from pytest import MonkeyPatch

from llama_index.embeddings.oci_genai import OCIGenAIEmbeddings


class MockResponseDict(dict):
    def __getattr__(self, val) -> Any:  # type: ignore[no-untyped-def]
        return self[val]


@pytest.mark.parametrize(
    "test_model_id", ["cohere.embed-english-light-v3.0", "cohere.embed-english-v3.0"]
)
def test_embedding_call(monkeypatch: MonkeyPatch, test_model_id: str) -> None:
    """Test valid call to OCI Generative AI embedding service."""
    oci_gen_ai_client = MagicMock()
    embedding = OCIGenAIEmbeddings(
        model_name=test_model_id,
        service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
        client=oci_gen_ai_client,
    )

    def mocked_response(invocation_obj):  # type: ignore[no-untyped-def]
        docs = invocation_obj.inputs

        embeddings = []
        for d in docs:
            if "Hello" in d:
                v = [1.0, 0.0, 0.0]
            elif "World" in d:
                v = [0.0, 1.0, 0.0]
            else:
                v = [0.0, 0.0, 1.0]
            embeddings.append(v)

        return MockResponseDict(
            {"status": 200, "data": MockResponseDict({"embeddings": embeddings})}
        )

    monkeypatch.setattr(embedding._client, "embed_text", mocked_response)

    output = embedding.get_text_embedding_batch(["Hello", "World"])
    correct_output = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]

    assert output == correct_output
