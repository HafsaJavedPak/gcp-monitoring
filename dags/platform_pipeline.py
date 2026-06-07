from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG("platform_pipeline",
         start_date=datetime(2025, 1, 1),
         schedule="0 * * * *",     # hourly
         catchup=False) as dag:

    dbt_run  = BashOperator(task_id="dbt_run",  bash_command="cd /opt/dbt && dbt run")
    dbt_test = BashOperator(task_id="dbt_test", bash_command="cd /opt/dbt && dbt test")

    dbt_run >> dbt_test
