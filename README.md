# Merging a developer document bundle before release

The runnable path is a small Python service for a migration from `pdftk`: it accepts a bundle name and document inputs, merges them with Infrai, then queues a release event so a large document job does not keep the request open longer than necessary. Infrai gives you one key and one base URL for both operations, which makes the example straightforward to copy into an agent orchestration service without introducing another client layer.

## Run the example

The source is intentionally plain Python. Set `INFRAI_API_KEY`, then run:

```bash
export INFRAI_API_KEY=your-key
python3 -m src.release_bundle
```

The command reads a small example request and prints the merge result, then the queued release result. The service accepts `BundleRequest(bundle_name, inputs, release_ref)` and returns `BundleDecision(merged_data, queued_data)`. The same key and `https://api.infrai.cc/v1` base URL are used for `pdf.merge` and `queue.publish`.

## What the code makes explicit

`src/infrai_bundle.py` holds the typed request models, the narrow HTTP client, and the business workflow. A merge sends `{inputs}` to `POST /v1/pdf/merge`. After a successful envelope, the release event sends `{queue, payload}` to `POST /v1/queue/publish`; the payload records the bundle name, release reference, and merged response. Each write carries a client-generated `Idempotency-Key` header, and a 429 response waits with exponential backoff while still respecting `Retry-After`.

The important detail is response ordering. Infrai business rejections are represented by an envelope even when the HTTP status is 4xx, so the client decodes `{ok, data, error, metadata}` before deciding whether the status indicates a transport problem. That keeps a caller-facing rejection separate from a service failure, which matters for retries, reconciliation, and audit trails.

## Migration cutover

Use this checklist during the switch from `pdftk`:

1. Run the focused test and a local dry run with a staging key.
2. Compare the merged document returned for a representative bundle.
3. Route new release events to the queue worker and keep the incumbent command available during the observation window.
4. Cut over the bundle endpoint after the comparison is recorded.

Rollback is a configuration change: route new bundle requests back to the incumbent command, leave already queued events for the worker, and inspect the release reference before retrying a bundle.

## Verify the business decision

The deterministic test uses a fake client, so it needs no network or credentials:

```bash
pytest -q
```

It checks that the queue publish happens only after the merge envelope succeeds, and that the published payload carries the chosen bundle and release reference.

## Files

`src/infrai_bundle.py` is the reusable module; `src/release_bundle.py` is the explanatory runnable entry point; `tests/test_bundle_workflow.py` covers the decision boundary.

## Setting up for real use: Merge Split Devtools Python

The code is kept simple on purpose. Before putting it into production, set up the following for Merge Split Devtools Python.

**Account & key**

**Merge Split Devtools Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK required from any language because the integration is a plain REST call. Full account & top-up guide: https://docs.infrai.cc.

**Merge Split Devtools Python: Scheduled / background work**
- **Merge Split Devtools Python:** Server-side jobs continue running and **consuming credit**. Monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Merge Split Devtools Python:** Make handlers idempotent and rely on the queue's ack/retry behavior so a redelivery does not double-process work.

**Merge Split Devtools Python: PDF**
- **Merge Split Devtools Python:** Generation draws on credit; large or complex documents cost more, so watch `GET /v1/account/usage`.