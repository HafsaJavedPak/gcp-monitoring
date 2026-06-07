import os, json, uuid, random
from datetime import datetime, timezone, timedelta
from flask import Flask
from google.cloud import pubsub_v1

app = Flask(__name__)
publisher = pubsub_v1.PublisherClient()
TOPIC = publisher.topic_path(os.environ["PROJECT_ID"], "work-orders-raw")

MAKES = {"Toyota": ["Corolla", "Camry"], "Ford": ["F-150", "Focus"],
         "Honda": ["Civic", "CR-V"], "BMW": ["3 Series", "X5"]}
SERVICES = ["Oil Change", "Brake Replacement", "Tire Rotation",
            "Engine Diagnostic", "Transmission Repair"]
STATUSES = ["open", "in_progress", "completed", "cancelled"]


def make_event():
    make = random.choice(list(MAKES))
    labor_hours = round(random.uniform(0.5, 8.0), 1)
    labor_cost = round(labor_hours * 95, 2)
    parts_cost = round(random.uniform(20, 1200), 2)
    created = datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 600))
    return {
        "work_order_id": str(uuid.uuid4()),
        "shop_id": f"shop_{random.randint(1, 5)}",
        "customer_id": f"cust_{random.randint(1000, 9999)}",
        "vehicle_make": make,
        "vehicle_model": random.choice(MAKES[make]),
        "vehicle_year": random.randint(2008, 2024),
        "service_type": random.choice(SERVICES),
        "status": random.choice(STATUSES),
        "labor_hours": labor_hours,
        "parts_cost": parts_cost,
        "labor_cost": labor_cost,
        "total_cost": round(parts_cost + labor_cost, 2),
        "technician_id": f"tech_{random.randint(1, 12)}",
        "created_at": created.isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@app.route("/", methods=["POST", "GET"])
def generate():
    n = random.randint(5, 20)
    futures = []
    for _ in range(n):
        future = publisher.publish(TOPIC, json.dumps(make_event()).encode("utf-8"))
        futures.append(future)
    # Block until every message is actually sent. Without this, Cloud Run scales
    # the instance to zero the moment the request returns, killing the async
    # Pub/Sub client's background flush thread before the messages leave the box.
    for future in futures:
        future.result()
    print(json.dumps({"severity": "INFO", "message": f"published {n} events"}))
    return f"published {n} events", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
