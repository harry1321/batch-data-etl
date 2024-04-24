# Overview

The objective of this project is to autonomously retrieve data from an open-source database daily for subsequent utilization in data visualization and analysis. This repository is dedicated to the data engineering architecture and setup, using Apache Airflow to orchestrate a batch data processing pipeline. Additionally, all data from each run is stored in Google Cloud Storage.

1. **Data Extraction**: Download a batch of .xml.gz files and extract vehicle speed, traffic volume, and vehicle occupancy data from the .xml files contained within.
2. **Data Cleaning**: Apply a variety of rules to filter out unqualified data and employ the moving average method to impute those data points.
3. **Data Transform**: Aggregate the data to adjust the time interval from 1 minute to 5 minutes, as reducing the interval decreases data fluctuations.
4. **Data Loading**: Load transformed data into Google Cloud Storage.

# Architecture

![architecture.png](/assets/architecture.png)
# Files

- `/dags` : Contains the following Python scripts to implement the batch data ETL workflow.
    - `/tasks` : All the task functions are include in this folder.
        - `extract.py` : Functions to extract target data from open source database.
        - `clean_transform.py` : Functions to clean and transform data for loading into a Google Cloud Storage bucket.
        - `read_load.py` : Functions to load the clean data to Google Cloud Storage services.
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

1. Have Docker installed on your system
2. Have all the required packages written in `requirements.txt` 
3. Have your own Google Cloud Platform account and get credentials to store or access files in Google Cloud Storage.
4. Set up a new project and storage bucket, and then set the Airflow Variables in `.env` 

# Dependencies

- Python
- Pandas
- Google Cloud Storage
