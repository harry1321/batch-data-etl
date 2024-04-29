from datetime import datetime, timedelta

from tasks.extract import GenData
from tasks.clean_transform import CleanTool
from tasks.read_load_gcp import GCSBucket, GCBigQuery

def task_date(**kwargs):
    # 以2021/05/30為例 格式為 date="20210530"
    execute_date = kwargs['logical_date']
    execute_date = execute_date.strftime('%Y%m%d')
    return {'date':execute_date}

def task_gen(ti):
    """
    Extract data from XML file on a open database and write them to files.
    XCom pull date to specify the day for which you want to extract the data.
    """
    temp = ti.xcom_pull(task_ids="date")
    date = temp.get("date")
    extract = GenData()
    extract.gen_data(date)

def task_clean(ti):
    """
    Clean the data on local and write them to a new file.
    XCom pull date to specify the day for which you want to clean the data.
    """
    temp = ti.xcom_pull(task_ids="date")
    date = temp.get("date")
    sweep = CleanTool(date,'1')
    ratio = sweep.preprocess_data()
    sweep.transform()
    sweep.save()
    return {"error_ratio":ratio}

def task_load_gcs(data_state,ti):
    temp = ti.xcom_pull(task_ids="date")
    date = temp.get("date")
    gcs = GCSBucket()
    gcs.upload_directory(source_directory=f"/opt/airflow/data/{data_state}/{date}", prefix=f"{data_state}/{date}")

def task_branch(success_route, failed_route, ti):
    temp = ti.xcom_pull(task_ids="clean")
    if temp.get("error_ratio") > 1:
        print(f"Did not pass data quality test with data error ratio {temp.get('error_ratio')}")
        return f"{failed_route}"
    else:
        print(f"Did not pass data quality test with data error ratio {temp.get('error_ratio')}")
        return f"{success_route}"

def task_load_bq(dataset_name, table_name, bucket_name, ti):
    temp = ti.xcom_pull(task_ids="date")
    date = temp.get("date")
    gbq = GCBigQuery(dataset_name)
    gbq.load_from_bucket(table_name=table_name, bucket_name=bucket_name, prefix=f"processed/{date}/")