from datetime import datetime,timedelta

from airflow.models import DAG
# Operators
from airflow.operators.python import PythonOperator

from tasks.task_functions import task_date, task_gen, task_clean

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

date >> gen >> clean