import os, json, base64
from datetime import datetime, timezone
from flask import Flask, request
from google.cloud import bigquery

app = Flask(__name__)
bq = bigquery.Client()
TABLE = f'{os.environ["PROJECT_ID"]}.raw.work_orders'
REQUIRED = {"work_order_id", "shop_id"}


@app.route("/healthz")
def health():
    return "ok", 200


@app.route("/", methods=["POST"])
def ingest():
    envelope = request.get_json(silent=True)
    if not envelope or "message" not in envelope:
        log("ERROR", "bad_pubsub_envelope")
        return "bad request", 400
    try:
        payload = base64.b64decode(envelope["message"]["data"]).decode("utf-8")
        row = json.loads(payload)
    except Exception as e:
        log("ERROR", f"decode_failed: {e}")
        return "", 204  # ack so Pub/Sub doesn't redeliver garbage forever

    if not REQUIRED.issubset(row):
        log("ERROR", f"schema_validation_failed: missing {REQUIRED - set(row)}")
        return "", 204

    row["ingested_at"] = datetime.now(timezone.utc).isoformat()
    errors = bq.insert_rows_json(TABLE, [row])
    if errors:
        log("ERROR", f"bigquery_insert_failed: {errors}")
        return "insert failed", 500  # 5xx -> Pub/Sub retries
    log("INFO", "row_ingested")
    return "", 204


def log(severity, message):
    print(json.dumps({"severity": severity, "message": message}))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
