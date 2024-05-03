from datetime import datetime

import pandas as pd

from google.cloud import bigquery

from variables import GCP_CREDENTIALS_FILE_PATH, GCP_PROJECT_ID, DATASET_NAME, TABLE_NAME

SCHEMA = [
    bigquery.SchemaField("time","TIMESTAMP"),
    bigquery.SchemaField("vd","STRING"),
    bigquery.SchemaField("volume","FLOAT"),
    bigquery.SchemaField("speed","FLOAT"),
    bigquery.SchemaField("occupancy","FLOAT"),
]

class GCBigQuery():
    def __init__(self, dataset_name=DATASET_NAME, credentials_file=GCP_CREDENTIALS_FILE_PATH):
        self.bq_client = bigquery.Client.from_service_account_json(credentials_file)
        self.dataset_name = dataset_name

    def standard_query(self, start_date, end_date, weekdays=None, stime=None, etime=None, locations=None, table_name=TABLE_NAME) -> str:
        clause=f"WHERE V.D >= '{start_date}' AND V.D <= '{end_date}'"
        if isinstance(weekdays,list):
            if len(weekdays) > 1:
                sub_clause = ""
                for w in weekdays[:-1]:
                    sub_clause += f" V.W = {w} OR"
                sub_clause += f" V.W = {weekdays[-1]}"
                clause += f" AND ({sub_clause})"
            else:
                clause += f" AND (V.W = {weekdays[0]})"
        if isinstance(stime,str):
            clause += f" AND V.H >= '{stime}'"
        if isinstance(etime,str):
            clause += f" AND V.H <= '{etime}'"
        if isinstance(locations,list):
            if len(locations) > 1:
                sub_clause = ""
                for l in locations[:-1]:
                    sub_clause += f"'{l}', "
                sub_clause += f"'{locations[-1]}'"
                clause += f" AND (V.vd IN ({sub_clause}))"
            else:
                clause += f" AND (V.vd = '{locations[0]}')"
            
        clause=clause+" ORDER BY V.time_tz"
        sql = f"""
            WITH V AS(
            SELECT *, STRING(time, "Asia/Taipei") AS time_tz, DATETIME(time, "Asia/Taipei") AS D, MOD(EXTRACT(DAYOFWEEK FROM DATETIME(time, "Asia/Taipei"))+5, 7) AS W, TIME(time, "Asia/Taipei") AS H
            FROM {GCP_PROJECT_ID}.{self.dataset_name}.{table_name}
            )
            SELECT time_tz, V.vd, V.volume, V.speed, V.occupancy FROM V
            {clause}
        """
        return sql

    def query(self, sql) -> pd.DataFrame:
        query_job = self.bq_client.query(sql)
        query_result = query_job.to_dataframe()
        return query_result

