from datetime import datetime,timedelta

from airflow.models import DAG
# Operators
from airflow.operators.python import PythonOperator, BranchPythonOperator

from tasks.task_functions import task_date, task_gen, task_clean, task_branch, task_upload, task_load_bq
from tasks.read_load_gcp import GCP_CREDENTIALS_FILE_PATH, GCP_PROJECT_ID, BUCKET_NAME, BUCKET_CLASS, BUCKET_LOCATION

default_args={
    "owner": 'Harry Yang',
    'start_date': datetime(2024, 4, 20, 0, 0),
    'schedule_interval': '0 5 * * *',
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="batch_data_etl",
    default_args=default_args,
    catchup=False
) as dag:
    date = PythonOperator(
        task_id="date",
        python_callable=task_date
    )

    gen = PythonOperator(
        task_id="gen",
        python_callable=task_gen
    )

    clean = PythonOperator(
        task_id="clean",
        python_callable=task_clean
    )

    branch = BranchPythonOperator(
        task_id="branch",
        python_callable=task_branch,
        op_kwargs={"success_route":"upload_processed", "failed_route":"upload_unprocessed"}
    )

    load_gcs_processed = PythonOperator(
        task_id="upload_processed",
        python_callable=task_upload,
        op_kwargs={"data_state":"processed"}
    )
    
    load_gcs_unprocessed = PythonOperator(
        task_id='upload_unprocessed',
        python_callable=task_upload,
        op_kwargs={"data_state":"unprocessed"}
    )

    load_bq = PythonOperator(
        task_id="load_bq",
        python_callable=task_load_bq,
        op_kwargs={"dataset_name":"test", "table_name":"test", "bucket_name":f"{BUCKET_NAME}"}
    )
date >> gen >> clean >> branch >> [load_gcs_processed, load_gcs_unprocessed]
load_gcs_processed >> load_bq
