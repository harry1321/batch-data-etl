import os
import pandas as pd

GCP_CREDENTIALS_FILE_PATH = './google/credentials/google_credentials.json'
GCP_PROJECT_ID = 'principal-rope-420002'
DATASET_NAME = 'test'
TABLE_NAME = 'test'

vd_name = pd.read_csv("https://raw.githubusercontent.com/harry1321/Traffic-Dashboard/test/data/vd_static_mainline.csv")
vd_id = [vd_name.iloc[i,0].split('-')[3] for i in range(vd_name.shape[0])]
vd_name = [vd_name.iloc[i,0] for i in range(vd_name.shape[0])]
vd_dict = dict(zip(vd_name,vd_id))