# Incident Runbook — Work Orders Pipeline

## Alert: "Ingestor errors > 0"
1. Open Logs Explorer, filter service=ingestor severity=ERROR.
2. Identify failure class: decode_failed | schema_validation_failed | bigquery_insert_failed.
3. If bigquery_insert_failed -> check BigQuery quota/schema drift; messages retry automatically.
4. If schema_validation_failed -> inspect dead-letter topic `work-orders-dlq`; fix generator/schema.

## Alert: "Pub/Sub backlog growing" (unacked messages rising)
1. Check ingestor is up (uptime check + Cloud Run revision status).
2. If down: redeploy last good revision: `gcloud run services update-traffic ingestor --to-latest`.
3. Backlog drains automatically once the consumer is healthy; monitor unacked count to zero.

## Alert: "Uptime check failing"
1. Hit /healthz manually. Check Cloud Run logs for crash loops / OOM.
2. Roll back: `gcloud run revisions list` -> route traffic to last healthy revision.

## dbt test failure
1. Read failing test (e.g. not_null on work_order_id).
2. Inspect raw.work_orders for the offending rows; trace back to generator/ingestor.
3. Re-run: `dbt run --select <model>+ && dbt test --select <model>+`.
