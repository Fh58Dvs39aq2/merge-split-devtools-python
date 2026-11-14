from __future__ import annotations

import json

from .infrai_bundle import BundleRequest, InfraiHttpClient, release_bundle


def main() -> None:
    request = BundleRequest(
        bundle_name="sdk-reference",
        inputs=[
            "JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFtdIC9Db3VudCAwID4+CmVuZG9iagp4cmVmCjAgMwowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9Sb290IDEgMCBSIC9TaXplIDMgPj4Kc3RhcnR4cmVmCjExNQolJUVPRgo=",
            "JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFtdIC9Db3VudCAwID4+CmVuZG9iagp4cmVmCjAgMwowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9Sb290IDEgMCBSIC9TaXplIDMgPj4Kc3RhcnR4cmVmCjExNQolJUVPRgo=",
        ],
        release_ref="release-2026-10",
    )
    result = release_bundle(request, InfraiHttpClient())
    print(json.dumps({"merge": result.merged_data, "queue": result.queued_data}, indent=2))


if __name__ == "__main__":
    main()
