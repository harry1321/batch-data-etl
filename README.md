# Overview

---

The objective of this project is to autonomously retrieve data from an open-source database daily for subsequent utilization in data visualization and analysis. This repository is dedicated to the data engineering architecture and setup, using Apache Airflow to orchestrate a batch data processing pipeline. Additionally, all data from each run is stored in Google Cloud Storage.

1. **Data Extraction**: Download a batch of .xml.gz files and extract vehicle speed, traffic volume, and vehicle occupancy data from the .xml files contained within.
2. **Data Cleaning**: Apply a variety of rules to filter out unqualified data and employ the moving average method to impute those data points.
3. **Data Transform**: Aggregate the data to adjust the time interval from 1 minute to 5 minutes, as reducing the interval decreases data fluctuations.
4. **Data Loading**: Load transformed data into Google Cloud Storage.

# **Architecture**

![architecture.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/b30abf31-1973-404d-9af0-238ebdc05988/dd51406f-0600-4a5b-a303-1e2cd6ad74c5/architecture.png)