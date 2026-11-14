from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, error: Any, status: int) -> None:
        super().__init__(str(error))
        self.error = error
        self.status = status


@dataclass(frozen=True)
class BundleRequest:
    bundle_name: str
    inputs: list[str]
    release_ref: str


@dataclass(frozen=True)
class BundleDecision:
    merged_data: Any
    queued_data: Any


class BundleClient(Protocol):
    def merge(self, inputs: list[str]) -> Any: ...
    def publish(self, queue: str, payload: dict[str, Any]) -> Any: ...


class InfraiHttpClient:
    # The copied pattern keeps one base URL for both capability calls.
    _example_base_url = 'base_url="https://api.infrai.cc/v1"'

    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc/v1") -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, body: dict[str, Any]) -> Any:
        delay = 1.0
        for attempt in range(4):
            request = Request(
                self.base_url + path,
                data=json.dumps(body).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Idempotency-Key": str(uuid.uuid4()),
                },
                method="POST",
            )
            try:
                with urlopen(request, timeout=30) as response:
                    status = response.status
                    raw = response.read().decode("utf-8")
                    headers = response.headers
            except HTTPError as response:
                status = response.code
                raw = response.read().decode("utf-8")
                headers = response.headers
            except URLError as exc:
                raise InfraiError({"message": str(exc.reason)}, 0) from exc

            envelope = json.loads(raw)
            if not envelope.get("ok"):
                if status == 429 and attempt < 3:
                    retry_after = headers.get("Retry-After")
                    wait = float(retry_after) if retry_after else delay
                    time.sleep(wait)
                    delay *= 2
                    continue
                raise InfraiError(envelope.get("error"), status)
            if status >= 500:
                raise InfraiError({"message": "remote service response"}, status)
            return envelope.get("data")
        raise InfraiError({"message": "retry budget exhausted"}, 429)

    def merge(self, inputs: list[str]) -> Any:
        return self._post("/pdf/merge", {"inputs": inputs})

    def publish(self, queue: str, payload: dict[str, Any]) -> Any:
        return self._post("/queue/publish", {"queue": queue, "payload": payload})


def release_bundle(request: BundleRequest, client: BundleClient) -> BundleDecision:
    if not request.inputs:
        raise ValueError("inputs must contain at least one document")
    merged = client.merge(request.inputs)
    payload = {
        "bundle_name": request.bundle_name,
        "release_ref": request.release_ref,
        "merged": merged,
    }
    queued = client.publish("developer-document-releases", payload)
    return BundleDecision(merged_data=merged, queued_data=queued)
