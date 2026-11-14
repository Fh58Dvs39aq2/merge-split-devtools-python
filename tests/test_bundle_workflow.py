from src.infrai_bundle import BundleDecision, BundleRequest, release_bundle


class RecordingClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def merge(self, inputs: list[str]) -> dict[str, object]:
        self.calls.append(("merge", inputs))
        return {"document": "merged"}

    def publish(self, queue: str, payload: dict[str, object]) -> dict[str, object]:
        self.calls.append(("publish", (queue, payload)))
        return {"queued": True}


def test_release_publishes_only_after_merge() -> None:
    client = RecordingClient()
    request = BundleRequest("agent-docs", ["guide.pdf", "schema.pdf"], "r17")

    result = release_bundle(request, client)

    assert isinstance(result, BundleDecision)
    assert [name for name, _ in client.calls] == ["merge", "publish"]
    queue, payload = client.calls[1][1]
    assert queue == "developer-document-releases"
    assert payload["bundle_name"] == "agent-docs"
    assert payload["release_ref"] == "r17"
    assert payload["merged"] == {"document": "merged"}
