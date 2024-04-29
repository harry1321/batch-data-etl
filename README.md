# Overview

The objective of this project is to autonomously retrieve data from an open-source database daily for subsequent utilization in data visualization and analysis. This repository is dedicated to the data engineering architecture and setup, using Apache Airflow to orchestrate a batch data processing pipeline. All data from each run is stored in Google Cloud Storage, serving as a data lake, and subsequently utilized BigQuery as a data warehouse for data visualization.

1. **Data Extraction**: Download a batch of .xml.gz files and extract vehicle speed, traffic volume, and vehicle occupancy data from the .xml files contained within.
2. **Data Cleaning**: Apply a variety of rules to filter out unqualified data and employ the moving average method to impute those data points. Additionally, calculated a bad data ratio to assess data quality. Data failing to meet the threshold will undergo further review.
3. **Data Transform**: Aggregate the data to adjust the time interval from 1 minute to 5 minutes, as reducing the interval decreases data fluctuations.
4. **Data Loading**: Load the data into Google Cloud Storage, branching it into two directories. One directory is designated to store transformed and cleaned data, while the other is allocated for storing unqualified data.

# Architecture

![architecture.png](/assets/architecture.png)
# Files

- `/dags` : Contains the following Python scripts to implement the batch data ETL workflow.
    - `/tasks` : All the task functions are include in this folder.
        - `extract.py` : Functions to extract target data from open source database.
        - `clean_transform.py` : Functions to clean and transform data for loading into a Google Cloud Storage bucket.
        - `read_load.py` : Functions to load data to Google Cloud Storage and BigQuery.
        - `task_functions.py` : Functions used in the Airflow DAG.
    - `batch_data_etl.py` : Airflow DAG setup for orchestrating the ETL process.

# Run the Project

To run the project, follow these steps:

1. Build the Docker image using the provided `dockerfile` which copies the project files into the appropriate directory within the container.
    
    ```
    docker-compose build
    ```
    
2. Initialize the database
    
    ```
    docker-compose up airflow-init
    ```
    
3. Run Airflow
    
    ```
    docker-compose up -d
    ```

For more details about how to quickly deploy Airflow on docker, please refer to https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html.
# Requirements

1. Have Docker installed on your system.
2. Create these folders: `logs`, `plugins`, `config`, `data`, `google/credentials`.
3. Have all the required packages written in `requirements.txt` .
4. Have your own Google Cloud Platform account, and create a new project and storage bucket.
5. Get credentials to store or access files in Google Cloud Storage, and save the credentials.json under ./google/credentials .
6. Then set the necessary Airflow Variables in .env .

# Dependencies

- Python
- Pandas
- Google Cloud Storage
- Google Cloud BigQuery
