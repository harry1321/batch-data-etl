from datetime import datetime, timedelta

from tasks.extract import GenData
from tasks.clean_transform import *
from tasks.read_load_gcp import GCSBucket

def task_date(ti):
    # 以2021/05/30為例 格式為 date="20210530"
    execute_date = datetime.today() - timedelta(days=1)
    execute_date = execute_date.strftime('%Y%m%d')
    data_kind = ['flow','speed','occ']
    full_path_today = [f"{execute_date}_{kind}.csv" for kind in data_kind]
    # XCom push file name in gcs and date
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
    sweep.preprocess_data()
    sweep.transform()
    sweep.save()def task_upload(data_state,ti):
    temp = ti.xcom_pull(task_ids="date")
    date = temp.get("date")
    gcs = GCSBucket()
    gcs.upload_directory(source_directory=f"/opt/airflow/data/{data_state}/{date}", prefix=date)

def task_branch(success_route, failed_route, ti):
    temp = ti.xcom_pull(task_ids="clean")
    if temp.get("error_ratio") > 1:
        print(f"Did not pass data quality test with data error ratio {temp.get('error_ratio')}")
        return f"{failed_route}"
    else:
        print(f"Did not pass data quality test with data error ratio {temp.get('error_ratio')}")
        return f"{success_route}"