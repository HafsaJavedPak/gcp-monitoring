# GCP Observability-First Data Platform

All the code files for the platform build, in the folder layout the deploy
commands expect. Run the deploy commands from **this top-level folder** (the one
that contains `generator/` and `ingestor/`).

## Folder map

```
gcp-platform/
├── schema.json              # BigQuery raw.work_orders table schema (Block 3)
├── cloudbuild.yaml          # CI/CD recipe (Phase 7, stretch)
├── INCIDENT_RUNBOOK.md       # ops playbook (Phase 6)
├── generator/               # Cloud Run service: makes fake events -> Pub/Sub
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── ingestor/                # Cloud Run service: Pub/Sub -> validate -> BigQuery
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── dbt/                     # transformations (Phase 4, runs from your laptop)
│   ├── dbt_project.yml
│   ├── profiles.yml.example  # copy to ~/.dbt/profiles.yml
│   └── models/
│       ├── staging/
│       │   ├── stg_work_orders.sql
│       │   └── _sources.yml
│       └── marts/
│           └── revenue_by_shop_daily.sql
└── dags/                    # Airflow DAG (Phase 5, stretch)
    └── platform_pipeline.py
```

## Which file is used when

| File(s)                     | Used in            | How                                            |
|-----------------------------|--------------------|------------------------------------------------|
| `schema.json`               | Block 3            | `bq mk --table ... ./schema.json`              |
| `generator/`                | Block 4            | `gcloud run deploy generator --source ./generator` |
| `ingestor/`                 | Block 5            | `gcloud run deploy ingestor --source ./ingestor`   |
| `dbt/`                       | Phase 4            | `cd dbt && dbt run && dbt test`                |
| `dags/platform_pipeline.py` | Phase 5 (stretch)  | copied onto the Airflow VM                      |
| `cloudbuild.yaml`           | Phase 7 (stretch)  | run by the Cloud Build trigger on push to main |
| `INCIDENT_RUNBOOK.md`        | Phase 6            | lives in the repo; you walk it during incidents |

## dbt quick start (after rows are landing in BigQuery)

```bash
pip install dbt-bigquery
gcloud auth application-default login        # one-time local login
cp dbt/profiles.yml.example ~/.dbt/profiles.yml
cd dbt
dbt run
dbt test
```

## Changes from the original guide
- `cloudbuild.yaml`: fixed the `_RUNTIME_SA` substitution, which had a literal
  `PROJECT_ID` placeholder that would never resolve. Your real project ID is in.
- Added `dbt/dbt_project.yml` and `dbt/profiles.yml.example` so the dbt models
  run without extra scaffolding (the guide assumed `dbt init` generates these).
