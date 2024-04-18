from datetime import datetime,timedelta

from airflow.models import DAG
# Operators
from airflow.operators.python import PythonOperator, BranchPythonOperator

from tasks.task_functions import task_date, task_gen, task_clean, task_branch, task_upload

default_args={
    "owner": 'Harry Yang',
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="batch_data_etl",
    default_args=default_args
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

    upload_processed = PythonOperator(
        task_id="upload_processed",
        python_callable=task_upload,
        op_kwargs={"data_state":"processed"}
    )
    
    upload_unprocessed = PythonOperator(
        task_id='upload_unprocessed',
        python_callable=task_upload,
        op_kwargs={"data_state":"unprocessed"}
    )
date >> gen >> clean >> branch >> [upload_processed, upload_unprocessed]